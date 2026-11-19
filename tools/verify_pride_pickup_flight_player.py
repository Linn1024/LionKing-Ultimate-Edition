"""Verify the guarded fixed-pickup renderer through actual player windows and saves."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels
from pride_sprite_catalog import bitmap,md_frame,read_rom


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-flight-player/art-verification')
    parser.add_argument('--width',type=int,choices=(256,320),default=256)
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build');out.mkdir()
    base=ROOT/'build/pride-flight-player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    tape=ROOT/'engine/tapes/allbugsF.read.tape';config=out/'host.ini'
    config.write_text('opengl = 0\nscale = 3\n')
    choices={'native':'','frames':'graphics.sprites.pickups.frames = md\n',
        'palette':'graphics.sprites.pickups.palette = md\n','both':'graphics.sprites.pickups = md\n',
        'sibling':'graphics.hud = md\n'}
    profiles={}
    for name,choice in choices.items():
        profiles[name]=out/f'{name}.ini';profiles[name].write_text('schema = 1\ngame = snes\n'+
            ('display.viewport = md\n' if args.width==320 else '')+choice)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    md_rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    commands={};checks={};observations=[]
    def run(name,source,field,mode='aot',load=None,inputs=tape,save=None,binary=None):
        folder=out/name;folder.mkdir()
        cmd=[binary or base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profiles[source],'--config',config,'--input-polled',inputs,'--frames',field,
            '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
            '--dump-scene',folder/'scene.json','--wav',folder/'audio.wav','--wav-seconds',60]
        if mode=='lle':cmd+=['--lle']
        if load:cmd+=['--load',load]
        if save:cmd+=['--save-at',field,save]
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        return dict(pixels=pixels(folder/'window.png'),hashes=hashes(folder/'run.log'),
            scene=json.loads((folder/'scene.json').read_text()),pcm=wav_data(folder/'audio.wav'),folder=folder)
    def same(a,b):return all(a[key]==b[key] for key in ('pixels','hashes','scene','pcm'))
    for field,pose in ((1616,0xc528bc),(1780,0xc528dd)):
        results={s:run(f'{field}-{s}',s,field) for s in choices}
        native=results['native'];w,h,original=native['pixels'];assert (w,h)==(args.width*3,672)
        scene=native['scene'];assert scene['level']==0 and scene['latched_gameplay']['descriptor']==0x387
        pieces=[p for p in scene['pieces'] if p['pose']==pose and p['fixed'] and p['kept']]
        assert pieces and all(p['palette']==0 for p in pieces)
        center=(min(p['screen'][0] for p in pieces)+max(p['screen'][0]+p['size'] for p in pieces))//2
        distance=center-128;magnitude=abs(distance)
        side=0 if magnitude<=16 else 64 if magnitude>=64 else (magnitude-16)*64//48
        if distance<0:side=-side
        extra=(args.width-256)//2;shift=extra+int(extra*side/64)
        boxes=[((p['screen'][0]+shift)*3,p['screen'][1]*3,(p['screen'][0]+shift+p['size'])*3,(p['screen'][1]+p['size'])*3) for p in pieces]
        bx,by,bw,bh,_=bitmap(md_rom,md_frame(md_rom,{0xc528bc:0x94df4,0xc528dd:0x94e1c}[pose]),True,with_origin=True)
        piece=pieces[0];flipx=bool(piece['attributes']&0x4000);flipy=bool(piece['attributes']&0x8000)
        ox=piece['screen'][0]+piece['local'][0]+piece['size'] if flipx else piece['screen'][0]-piece['local'][0]
        oy=piece['screen'][1]+piece['local'][1]+piece['size']+1 if flipy else piece['screen'][1]-piece['local'][1]
        xs=[ox+(-x-1 if flipx else x)+shift for x in (bx,bx+bw-1)]
        ys=[oy-y-2 if flipy else oy+y for y in (by,by+bh-1)]
        art_boxes=boxes+[(min(xs)*3,min(ys)*3,(max(xs)+1)*3,(max(ys)+1)*3)]
        def inside(i,rectangles=boxes):
            x,y=i%w,i//w
            return any(a<=x<c and b<=y<d for a,b,c,d in rectangles)
        checks[f'{field}/guest_and_entire_pcm_unchanged']=all(r['hashes']==native['hashes'] and r['pcm']==native['pcm'] for r in results.values())
        changed={}
        for source in ('frames','palette','both'):
            diffs=[i for i,(a,b) in enumerate(zip(original,results[source]['pixels'][2])) if a!=b]
            changed[source]=len(diffs)
            checks[f'{field}/{source}_visible_and_confined']=bool(diffs) and all(inside(i,boxes if source=='palette' else art_boxes) for i in diffs)
        checks[f'{field}/frame_palette_independent']=results['both']['pixels']!=results['frames']['pixels'] and results['both']['pixels']!=results['palette']['pixels']
        checks[f'{field}/hud_choice_preserves_flight']=all(original[i]==results['sibling']['pixels'][2][i] for i in range(w*h) if inside(i))
        if args.width==256:
            old=ROOT/f'build/pride-pickup-flight-windows/{field}-snes.png'
            checks[f'{field}/native_client_unchanged']=pixels(old)==native['pixels']
        else:
            old=run(f'{field}-previous-native','native',field,binary=ROOT/'build/pride-player/player.exe')
            checks[f'{field}/native_client_unchanged']=same(old,native)
        checks[f'{field}/aot_lle_equal']=same(run(f'{field}-both-lle','both',field,'lle'),results['both'])
        state=out/f'flight-{field-1}.state'
        saved=run(f'{field}-save-native','native',field-1,save=state,binary=ROOT/'build/pride-player/player.exe')
        used=int(re.search(r'tape_words_used=(\d+)',(saved['folder']/'run.log').read_text()).group(1))
        suffix=out/f'after-{field-1}.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
        for mode in ('aot','lle'):
            loaded=run(f'{field}-loaded-{mode}','both',field,mode,load=state,inputs=suffix)
            checks[f'{field}/{mode}_save_graphics_change']=all(loaded[k]==results['both'][k] for k in ('pixels','hashes','scene'))
            checks[f'{field}/{mode}_save_pcm_exact']=loaded['pcm']==results['both']['pcm'][len(saved['pcm']):]
        observations.append(dict(field=field,pose=hex(pose),changed_pixels=changed,visible_fixed_pieces=pieces))
        print(field,changed,'failed:',[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,tape,ROOT/'engine/runner/tlk_pickup_flight_role.h',ROOT/'engine/runner/tlk_wide.c',
        ROOT/'engine/runner/tlk_resources.c',ROOT/'build/pride-pickup-flight-art2/report.json',
        ROOT/'build/pride-flight-baseline/report.json',ROOT/'build/pride-player/player.exe']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
