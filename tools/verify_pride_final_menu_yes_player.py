"""Verify installed MD confirmed-menu drawing in real Windows clients."""
import array
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-final-menu-player9');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-mixed-origin-probe/report.json';old=bound(source)
    reference=ROOT/'build/pride-continue-transition-reference/report.json';refs=bound(reference)
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';package=manifest.parent/json.loads(manifest.read_text())['menu_assets']['file']
    out=base/'yes';out.mkdir();checks={};commands={};wrong={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    bank_report=ROOT/'build/pride-continue-bank-ready-probe/capture/report.json';bound(bank_report)
    bank=bank_report.parent/'boot/bank.record'
    clean['TLK_CONTINUE_BANK_RECORD']=str(bank)
    env=dict(clean,TLK_FINAL_MD_ART='1')
    def run(width,confirm,age,label='',load=None,save=False,enabled=True,lle=False):
        name=f'{width}-{confirm}-{label or age}';folder=out/name;folder.mkdir()
        tape=out/f'{confirm}.tape'
        if not tape.exists():
            raw=bytearray(4800*2)
            for index in range(3894+confirm-1,3894+confirm+3):struct.pack_into('<H',raw,index*2,0x8000)
            tape.write_bytes(raw)
        cmd=old['commands']['selected-final'].copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--resource-profile',out/f'{width}.ini'),('--config',out/'host.ini'),('--frames',3894+age),
            ('--input',tape),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load/'saved.state')
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        cmd+=['--final-menu-assets',str(package)]
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env if enabled else clean,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[name]=cmd;checks[name+'_exit']=result.returncode==0
        print('Window',name,'exit',result.returncode,flush=True)
        return folder
    levels=[0,4,8,12,17,21,25,29];green=[0,8,17,25,34,42,51,59]
    expand=lambda v:((v<<3)|(v>>2))
    lookup={r<<11|g<<5|b:(expand(r),expand(levels[green.index(g)]),expand(b)) for r in levels for g in green for b in levels}
    for width in (256,320):
        (out/f'{width}.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        for confirm in (124,130):
            frames={};indices={r['age']:r for r in refs['cases'][str(confirm)]['video_frames']}
            for age in sorted({confirm,confirm+58,confirm+59,confirm+63,confirm+67,confirm+69,confirm+73,confirm+208,confirm+209,confirm+226,confirm+227}):
                frames[age]=run(width,confirm,age,save=age in (confirm+58,confirm+209))
                window=frames[age]/'window.png'
                if not window.exists():continue
                f=indices[age]
                with (reference.parent/str(confirm)/'video.bin').open('rb') as video:video.seek(f['offset']);raw=video.read(f['bytes'])
                expected=[]
                for y in range(224):expected.extend(lookup[v] for v in array.array('H',raw[y*f['pitch']:y*f['pitch']+640]))
                w,h,actual=pixels(window);start=(320-width)//2;different=0
                for y in range(448):
                    for x in range(width*2):
                        sx=x//2+start;sy=y//2
                        if 256<=sx<280 and 186<=sy<214:continue
                        different+=actual[y*width*2+x]!=expected[sy*320+sx]
                name=f'{width}-{confirm}-{age}';wrong[name]=different
                checks[name+'_original_outside_counter']=(w,h)==(width*2,448) and not different
            for saved,target in ((confirm+58,confirm+63),(confirm+209,confirm+226)):
                cold=run(width,confirm,target,label=f'cold{target}',load=frames[saved])
                if not (cold/'window.png').exists():continue
                checks[f'{width}-{confirm}-cold{target}_client']=pixels(cold/'window.png')==pixels(frames[target]/'window.png')
                checks[f'{width}-{confirm}-cold{target}_guest']=hashes(cold/'run.log')==hashes(frames[target]/'run.log')
                checks[f'{width}-{confirm}-cold{target}_pcm']=pcm(cold/'audio.wav')==pcm(frames[target]/'audio.wav')[len(pcm(frames[saved]/'audio.wav')):]
            native=run(width,confirm,confirm+73,label='native',enabled=False)
            checks[f'{width}-{confirm}_art_independent_guest']=hashes(native/'run.log')==hashes(frames[confirm+73]/'run.log')
            checks[f'{width}-{confirm}_art_independent_pcm']=pcm(native/'audio.wav')==pcm(frames[confirm+73]/'audio.wav')
    paths=[Path(__file__),build,source,reference,manifest,package,bank_report,bank]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,differing_pixels=wrong,
        excluded_original_comparison_rectangle=[256,186,24,28],credit_counts=[1,3],
        preparation_scope='Development fixture supplies a genuine previously captured Continue bank; full installed-bank migration remains open',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
