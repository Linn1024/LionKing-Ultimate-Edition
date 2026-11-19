"""Check real popup clients against original MD pixels, both HUD sides/widths."""
import argparse
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data
from pride_sprite_catalog import md_frame,bitmap

LEAF='graphics.sprites.effects.pickup_arrival'
NATIVE_POSES=[0xc6fd06,0xc6fd29,0xc6fd4c,0xc6fd73,0xc6fd94,0xc6fdbb,
              0xc6fde6,0xc6fe0b,0xc6fe30,0xc6fe55,0xc6fe7c,0xc6fe9d]
MD_POSES=[0xb864c,0xb8674,0xb869c,0xb86c4,0xb86ec,0xb8724]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',default='build/pride-popup-work/player-check')
    ap.add_argument('--build-report',default='build/pride-popup-work/commands4.json')
    args=ap.parse_args()
    out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT/'build');out.mkdir()
    candidate=ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'
    previous=ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'
    build_path=ROOT/args.build_report
    build=json.loads(build_path.read_text());assert digest(candidate)==build['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands=[];observations=[];seeds={}
    choices={'native':'','frames':f'{LEAF}.frames = md\n',
             'palette':f'{LEAF}.palette = md\n','position':f'{LEAF}.position = md\n',
             'art':f'{LEAF}.frames = md\n{LEAF}.palette = md\n',
             'all':f'{LEAF} = md\n','hud':'graphics.hud.palette = md\n'}
    md=(ROOT/'Lion King, The (World).md').read_bytes()
    md_images=[bitmap(md,md_frame(md,p),True,with_origin=True) for p in MD_POSES]
    colors=[]
    for c in struct.unpack_from('>16H',md,0x1d78aa):
        rgb=[]
        for shift in (1,5,9):
            v=c>>shift&7;v=v*4+(v>>2);rgb.append((v<<3)|(v>>2))
        colors.append(tuple(rgb))
    def run(name,field,width=256,choice='native',seed=None,save=None,binary=candidate,lle=False):
        folder=out/name;folder.mkdir()
        profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\n'+
            ('display.viewport = md\n' if width==320 else '')+choices[choice])
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--frames',field,
             '--input-polled',seed[1] if seed else tape,'--no-pace','--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json',
             '--wav',folder/'audio.wav','--wav-seconds',60]
        if seed:cmd+=['--load',seed[0]]
        if save:cmd+=['--save-at',field,save]
        if lle:cmd+=['--lle']
        commands.append(list(map(str,cmd)))
        current_env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=current_env,stdout=log,
                           stderr=subprocess.STDOUT,timeout=180,check=True)
        return dict(folder=folder,pixels=pixels(folder/'window.png'),hashes=hashes(folder/'run.log'),
                    pcm=wav_data(folder/'audio.wav'),scene=json.loads((folder/'scene.json').read_text()),
                    coverage=json.loads((folder/'sprites.json').read_text()))
    for side,start in [('right',1654),('left',1800)]:
        state=out/f'{side}.state'
        saved=run(f'seed-{side}',start,save=state,binary=previous)
        used=int(re.search(r'tape_words_used=(\d+)',(saved['folder']/'run.log').read_text()).group(1))
        suffix=out/f'{side}.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
        seeds[side]=(state,suffix)
    seen={'right':set(),'left':set()}
    for side,fields in [('right',(1664,1668,1672,1680,1684,1692)),
                        ('left',(1804,1812,1820,1824,1832,1836))]:
        for width in (256,320):
            for field in fields:
                label=f'{side}/{width}/{field}'
                native=run(label.replace('/','-')+'-native',field,width,seed=seeds[side])
                mixed=run(label.replace('/','-')+'-md',field,width,'all',seeds[side])
                pieces=[p for p in native['scene']['pieces'] if p['fixed'] and p['kept'] and p['pose'] in NATIVE_POSES]
                assert pieces,(label,'No displayed popup')
                pose=pieces[0]['pose'];phase=NATIVE_POSES.index(pose)//2;seen[side].add(phase)
                checks[label+'/state_and_pcm']=len(native['hashes'])==2 and native['hashes']==mixed['hashes'] and native['pcm']==mixed['pcm']
                checks[label+'/visible_source_change']=native['pixels']!=mixed['pixels']
                w,h,pixels_md=mixed['pixels'];checks[label+'/dimensions']=(w,h)==(width*3,672)
                # Screen-fixed anchors are positioned by the viewport, not camera X.
                anchor_x=width-26 if side=='right' else 18
                bx,by,bw,bh,data=md_images[phase]
                mismatches=[];opaque=0
                for i,c in enumerate(data):
                    if not c:continue
                    x=anchor_x+bx+i%bw;y=20+by+i//bw
                    if not (0<=x<width and 0<=y<224):continue
                    actual=pixels_md[(y*3+1)*w+x*3+1]
                    opaque+=1
                    if actual!=colors[c]:mismatches.append((x,y,actual,colors[c]))
                checks[label+'/original_md_pixels']=opaque>0 and not mismatches
                observations.append(dict(label=label,native_pose=hex(pose),md_pose=hex(MD_POSES[phase]),
                    opaque_pixels=opaque,mismatches=mismatches[:12],pieces=pieces))
                print(label,'phase',phase,'pixel mismatches',len(mismatches),flush=True)
    for side,phases in seen.items():checks[side+'/all_six_md_phases']=phases==set(range(6))
    # Independent leaves, native control, and a cold save in the visible effect.
    for side,field in [('right',1680),('left',1824)]:
        rows={choice:run(f'independent-{side}-{choice}',field,choice=choice,seed=seeds[side]) for choice in choices}
        native=rows['native']
        checks[side+'/all_leaves_keep_state_pcm']=all(r['hashes']==native['hashes'] and r['pcm']==native['pcm'] for r in rows.values())
        checks[side+'/frame_palette_independent']=len({tuple(rows[c]['pixels'][2]) for c in ('frames','palette','art')})==3
        checks[side+'/position_independent']=rows['position']['pixels']!=native['pixels'] and rows['all']['pixels']!=rows['art']['pixels']
        old=run(f'previous-{side}',field,seed=seeds[side],binary=previous)
        checks[side+'/native_client_unchanged']=old['pixels']==native['pixels']
        state=out/f'{side}-active.state'
        saved=run(f'active-save-{side}',field-1,seed=seeds[side],save=state)
        used=int(re.search(r'tape_words_used=(\d+)',(saved['folder']/'run.log').read_text()).group(1))
        suffix=out/f'{side}-active.polled.tape';suffix.write_bytes(seeds[side][1].read_bytes()[used*2:])
        for lle in (False,True):
            resumed=run(f'active-resume-{side}-{int(lle)}',field,choice='all',seed=(state,suffix),lle=lle)
            checks[f'{side}/active_save_{lle}']=all(resumed[k]==rows['all'][k] for k in ('hashes','pixels'))
    paths=[Path(__file__),build_path,ROOT/'build/pride-popup-work/guards4/report.json',
           ROOT/'build/pride-popup-art-review/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
                full_first_level_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
