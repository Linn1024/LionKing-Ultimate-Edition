"""Verify scene-owned pixels against original art and original MD palette observations."""
import argparse
import array
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return list(csv.DictReader(path.open()))


def art_file(path, magic):
    data=path.read_bytes();assert data[:8]==magic
    version,count=struct.unpack_from('<II',data,8);assert version==1
    at=16;result={}
    for _ in range(count):
        pose,x,y,w,h=struct.unpack_from('<IiiII',data,at);at+=20
        a=data[at:at+w*h];at+=w*h;b=data[at:at+w*h];at+=w*h
        result[pose|0xc00000]=(x,y,w,h,a,b)
    assert at==len(data)
    return result


def rgb(color):
    c=[(color>>s)&31 for s in (0,5,10)]
    a=[v*8+v//4 for v in c]
    return a[0]<<16|a[1]<<8|a[2]


def verify_pixels(folder, width, frames_md, palettes_md, expected_count, authentic_gpu=False):
    original=ROOT/'build/pride-death-controller/original-palettes.csv'
    scalar={}
    for r in rows(original):
        if r['case']!='0':continue
        age=int(r['age']);cub=int(r['index'])<16
        source=int(r['next_color'] if age>=270 else r['death_color']);actual=int(r['actual'])
        for shift in (0,3,6):
            key=(age,cub,(source>>shift)&7);value=(actual>>shift)&7
            assert key not in scalar or scalar[key]==value
            scalar[key]=value
    def fade(c, age, cub, md):
        age=min(age,345)
        out=0
        for shift in (0,5,10):
            v=(c>>shift)&31
            if md:
                q=v//4;assert v==q*4+q//4, (age,c,shift)
                q=scalar[age,cub,q];v=q*4+q//4
            elif age>=270:v=min(v,4*((age-270)//3))
            else:
                losses=0 if cub and age<225 else (age-225+2)//3 if cub else (age+2)//3 if age<24 else 8
                v=max(0,v-4*losses)
            out|=v<<shift
        return rgb(out)
    death=art_file(ROOT/'build/pride-owned-death-art/original-bitmaps.bin',b'TLKDART1')
    revival=art_file(ROOT/'build/pride-owned-revival-art/original-bitmaps.bin',b'TLKRART1')
    poses={int(r['age']):int(r['snes_pose']) for r in rows(ROOT/'build/pride-death-controller/original-fields.csv') if r['case']=='0'}
    poses.update({int(r['age']):int(r['snes_pose']) for r in rows(ROOT/'build/pride-revival-scene/original-revival.csv') if r['case']=='0'})
    mdrom=(ROOT/'Lion King, The (World).md').read_bytes()
    mdpalette=[]
    for i in range(16):
        raw=int.from_bytes(mdrom[0x1d78aa+i*2:0x1d78ac+i*2],'big')
        mdpalette.append(sum((((raw>>s)&7)*4+((raw>>s)&7)//4)<<d for s,d in ((1,0),(5,5),(9,10))))
    count=width*224;compared=0;ages=[];first_xy=None;observed_md=False;observed_snes=False
    with (folder/'render-owned.rgb').open('rb') as f:
        assert f.read(8)==b'PRDRGB01' and struct.unpack('<II',f.read(8))==(width,224)
        while header:=f.read(24):
            age,pose,x,y,flip,md=struct.unpack('<IIiiII',header);assert age==len(ages) and md==palettes_md
            palette=struct.unpack('<16H',f.read(32))
            full=array.array('I');full.frombytes(f.read(count*4))
            tags=array.array('I');tags.frombytes(f.read(count*4))
            actual=array.array('I');actual.frombytes(f.read(count*4))
            assert len(full)==len(tags)==len(actual)==count
            assert all((tag&0xffffff) in (0,0x00ff00,0xff0000) and tag>>24<=1 for tag in tags)
            observed_md|=any((t&0xffffff)==0xff0000 for t in tags);observed_snes|=any((t&0xffffff)==0x00ff00 for t in tags)
            lut={}
            for c,t in set(zip(full,tags)):
                color=(c>>19)&31 | ((c>>11)&31)<<5 | ((c>>3)&31)<<10
                lut[c,t]=fade(color,age,False,(t&0xffffff)==0xff0000)
            expected=array.array('I',(lut[c,t] for c,t in zip(full,tags)))
            if (age<249 or age>=270) and not(authentic_gpu and age==0):
                source_age=min(age,345)
                if authentic_gpu:
                    source_age=min(max(age-(1 if age<=24 else 2),0),224) if age<249 else min(max(270,age-2),345)
                assert pose==poses[source_age],(age,hex(pose),hex(poses[source_age]))
                bx,by,w,h,a,b=(death if age<249 else revival)[pose]
                if age<249:
                    if first_xy is None:first_xy=x,y
                    moves=max(0,min(201,age-(25 if authentic_gpu else 23)))
                    def toward(start,target):return start+max(-moves,min(moves,target-start))
                    assert (x,y)==(toward(first_xy[0],width//2),toward(first_xy[1],128)),(age,x,y)
                selected=mdpalette if md else palette
                colors=[fade(c,age,age<249,bool(md)) for c in selected]
                indexes=b if frames_md else a
                for py in range(h):
                    for px in range(w):
                        index=indexes[py*w+px]
                        dx=x+(-bx-px-1 if flip else bx+px);dy=y+by+py
                        if index and 0<=dx<width and 0<=dy<224 and not(tags[dy*width+dx]&0x01000000):expected[dy*width+dx]=colors[index]
            elif authentic_gpu and age==0:assert pose==0
            else:assert pose==0 and not any(actual)
            if expected!=actual:
                bad=next(i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b)
                raise AssertionError((age,bad%width,bad//width,hex(expected[bad]),hex(actual[bad]),hex(full[bad]),hex(tags[bad])))
            if age==270:assert not any(actual),'Health publication must still be black'
            compared+=count;ages.append(age)
    assert len(ages)==expected_count
    return dict(owned_fields=len(ages),pixels_compared=compared,md_base_palette_observed=observed_md,
                snes_base_palette_observed=observed_snes,black_reload_and_restore_verified=270 in ages)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profiles',nargs='+',choices=('native','frames','palette','all'),default=['native'])
    p.add_argument('--modes',nargs='+',choices=('control','owned'),default=['owned'])
    p.add_argument('--width',type=int,choices=(256,320),default=320)
    p.add_argument('--frames',type=int,default=5400);p.add_argument('--sdl',action='store_true');p.add_argument('--reuse',action='store_true')
    p.add_argument('--prepared',action='store_true',help='Use the excluded prepared-object/native-widget presenter')
    p.add_argument('--checkpoint',choices=('native','frames','palette','both'),
                   help='Independently select checkpoint sources in a separate output directory')
    p.add_argument('--revival-roar',choices=('snes','md'),default='snes',
                   help='Private full versus empty roar restoration, independent of artwork')
    p.add_argument('--output-root',type=Path,help='Separate evidence directory for a new source matrix')
    p.add_argument('--binary',type=Path,help='Use an isolated executable without replacing an installed target')
    p.add_argument('--execution',choices=('lle','aot'),default='lle')
    args=p.parse_args();host='sdl' if args.sdl else 'headless'
    family='scene-render-prepared' if args.prepared else 'scene-render'
    suffix='-checkpoint-'+args.checkpoint if args.checkpoint else ''
    if args.revival_roar=='md':suffix+='-roar-md'
    root=ROOT/args.output_root if args.output_root else ROOT/f'build/pride-{family}-{host}-{args.width}-{args.frames}{suffix}'
    root.mkdir(parents=True,exist_ok=True)
    report_path=root/'report.json';prior=json.loads(report_path.read_text()) if args.reuse else None
    binary=ROOT/args.binary if args.binary else ROOT/f'engine/build-win/tlk_scene_{"prepared" if args.prepared else "render"}_{"sdl" if args.sdl else "probe"}.exe';identity=digest(binary)
    if prior:assert prior['probe_sha256']==identity
    report_path.write_text('{"result":"RUNNING"}\n');runs={}
    config=root/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    for profile in args.profiles:
        for mode in args.modes:
            name=profile+'-'+mode;folder=root/name;folder.mkdir(exist_ok=True)
            settings='schema = 1\ngame = snes\ndisplay.viewport = '+('md' if args.width==320 else 'snes')+'\n'
            if profile=='frames':settings+='graphics.sprites.simba.cub.frames = md\n'
            if profile=='palette':settings+='graphics.sprites.simba.cub.palette = md\n'
            if profile=='all':settings+='graphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\ngraphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n'
            if args.checkpoint:
                settings+='graphics.sprites.checkpoints.frames = '+('md' if args.checkpoint in ('frames','both') else 'snes')+'\n'
                settings+='graphics.sprites.checkpoints.palette = '+('md' if args.checkpoint in ('palette','both') else 'snes')+'\n'
            resource=folder/'resources.ini';resource.write_text(settings)
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL'):env[key]='1'
            env['TLK_SCENE_RENDER_ENABLE']=str(int(mode=='owned'));env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
            env['TLK_SCENE_RESTORE_ROAR_ZERO']=str(int(args.revival_roar=='md'))
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',resource,'--frames',args.frames,'--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape']
            if args.execution=='lle':cmd.append('--lle')
            if args.sdl:cmd+=['--config',config,'--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100','--dump-window',folder/'window.png']
            else:cmd+=['--wide',args.width,'--wide-png',folder/'picture.png','--ram-log',folder/'route.ram']
            if args.reuse:
                for file,sha in prior['runs'][name]['artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
                for file,sha in prior['source_sha256'].items():
                    if file!='tools/probe_pride_scene_render.py':assert digest(ROOT/file)==sha,file
            else:
                capture={'probe_sha256':identity,'source_sha256':{str(f.relative_to(ROOT)).replace('\\','/'):digest(f) for f in
                    (ROOT/'tools/pride_scene_render_wide.c',ROOT/'tools/pride_scene_render_probe.c',ROOT/'tools/pride_scene_render_bridge.h',
                     ROOT/'tools/pride_scene_prepared_objects.c',ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h',
                     ROOT/'tools/pride_scene_restore_probe.c',ROOT/'tools/pride_scene_owner_probe.c',ROOT/'tools/pride_scene_prepare_probe.c',
                     ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',ROOT/'engine/runner/tlk_wide.c',
                     ROOT/'engine/runner/tlk_checkpoint_art.c',ROOT/'engine/runner/tlk_checkpoint_art.h',
                     ROOT/'engine/runner/tlk_checkpoint_role.h',ROOT/'engine/runner/tlk_resources.c',
                     ROOT/'engine/runner/tlk_resources.h',ROOT/'engine/runner/tlk_revival_art.c',
                     ROOT/'engine/runner/tlk_revival_art.h')},
                    'frames':args.frames,'width':args.width,'mode':mode,'execution':args.execution,'profile_sha256':digest(resource),'execution_completed':False}
                (folder/'capture.json').write_text(json.dumps(capture,indent=2)+'\n')
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
                assert digest(binary)==identity
                for file,sha in capture['source_sha256'].items():assert digest(ROOT/file)==sha,file
                capture['execution_completed']=True
                (folder/'capture.json').write_text(json.dumps(capture,indent=2)+'\n')
            fields=rows(folder/'render-fields.csv');unique={int(r['age']):r for r in fields}
            expected_count=len(unique);assert set(unique)==set(range(expected_count))
            if args.frames>=4783:
                assert 346<=expected_count<=354 if mode=='owned' else expected_count==346
                if mode=='owned':assert unique[expected_count-1]['released']=='1' and unique[expected_count-1]['native_pixel_mismatch']=='0'
            else:assert expected_count==args.frames-4429
            assert all(int(r['owned'])==(mode=='owned') for r in fields)
            result=verify_pixels(folder,args.width,profile in ('frames','all'),profile in ('palette','all'),expected_count,args.prepared) if mode=='owned' else {}
            if mode=='owned' and profile=='native' and args.checkpoint in ('palette','both'):
                assert result['md_base_palette_observed'],'MD checkpoint palette never reached owned composition'
            if args.frames==5400 and args.revival_roar=='snes':
                previous=ROOT/f'build/pride-scene-restore-{host}/native-canonical'
                assert hashes(folder/'run.log')==hashes(previous/'run.log')
                if args.sdl:assert wav_data(folder/'route.wav')==wav_data(previous/'route.wav')
                else:assert digest(folder/'route.ram')==digest(previous/'route.ram')
            if args.sdl:assert pixels(folder/'window.png')[:2]==(args.width*2,448)
            result.update(guest=hashes(folder/'run.log'),release_age=expected_count-1 if mode=='owned' and unique[expected_count-1]['released']=='1' else None,
                          artifacts_sha256={f.name:digest(f) for f in sorted(folder.iterdir()) if f.is_file()})
            runs[name]=result;print(host,args.width,name,result.get('pixels_compared',0),'owned pixel/reference and guest checks PASS',flush=True)
    assert digest(binary)==identity
    report_path.write_text(json.dumps(dict(result='OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN',scope=__doc__,
        host=host,width=args.width,frames=args.frames,execution=args.execution,probe_sha256=identity,runs=runs,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,
        capture_action='reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        prepared_objects=args.prepared,
        checkpoint_sources=args.checkpoint,
        revival_roar_source=args.revival_roar,
        source_sha256={str(f.relative_to(ROOT)).replace('\\','/'):digest(f) for f in
            (Path(__file__),ROOT/'tools/pride_scene_render_wide.c',ROOT/'tools/pride_scene_prepared_objects.c',
             ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h',ROOT/'tools/pride_scene_render_probe.c',
             ROOT/'tools/pride_scene_render_bridge.h',ROOT/'engine/runner/tlk_wide.c',ROOT/'engine/runner/tlk_revival_art.c',
             ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/CMakeLists.txt',
             ROOT/'engine/runner/tlk_checkpoint_art.c',ROOT/'engine/runner/tlk_checkpoint_art.h',
             ROOT/'engine/runner/tlk_checkpoint_role.h',ROOT/'engine/runner/tlk_resources.c',
             ROOT/'engine/runner/tlk_resources.h',ROOT/'engine/runner/tlk_revival_art.h',
             ROOT/'build/pride-death-controller/original-palettes.csv',ROOT/'build/pride-death-controller/original-fields.csv',
             ROOT/'build/pride-revival-scene/original-revival.csv',ROOT/'build/pride-owned-death-art/original-bitmaps.bin',
             ROOT/'build/pride-owned-revival-art/original-bitmaps.bin',ROOT/'build/pride-gpu-clock/visible-poses.json',
             ROOT/'build/pride-gpu-clock/report.json')}),indent=2)+'\n')


if __name__=='__main__':main()
