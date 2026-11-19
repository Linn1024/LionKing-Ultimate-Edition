"""Verify width-aware installed-menu HUDs, fades and save identities on Windows."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def transport_window(picture,width):
    w,h,image=picture
    if width==320:return picture
    result=image.copy()
    for y in range(352,448):
        hud=image[y*w+384:y*w+512]
        result[y*w+384:y*w+512]=[(0,0,0)]*128
        result[y*w+320:y*w+448]=hud
    return w,h,result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-final-menu-player10');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    oldbase=ROOT/'build/pride-final-menu-player9'
    reports={key:oldbase/key/'report.json' for key in ('continue','yes','no')}
    old={key:bound(path) for key,path in reports.items()}
    component=ROOT/'build/pride-final-menu-layout-component/verification/report.json';bound(component)
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';info=json.loads(manifest.read_text());package=manifest.parent/info['menu_assets']['file']
    bank=ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'
    out=base/'layout';out.mkdir();commands={};checks={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env=dict(clean,TLK_FINAL_MD_ART='1',TLK_CONTINUE_BANK_RECORD=str(bank))
    def run(width,kind,age,label=None,load=None,save=False,enabled=True,lle=False):
        name=f'{width}-{kind}-{label or age}';folder=out/name;folder.mkdir()
        if kind=='neutral':cmd=old['continue']['commands'][f'{width}-160'].copy()
        elif kind=='no':cmd=old['no']['commands']['160'].copy()
        else:cmd=old['yes']['commands'][f'{width}-124-197'].copy()
        if '--save-at' in cmd:
            at=cmd.index('--save-at');del cmd[at:at+3]
        cmd[0]=str(base/'player.exe')
        for flag,value in [('--resource-profile',out/f'{width}.ini'),('--config',out/'host.ini'),('--frames',3894+age),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        actual=env if enabled else {k:v for k,v in env.items() if k!='TLK_FINAL_MD_ART'}
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[name]=cmd;print(name,'exit',result.returncode,flush=True)
        return folder,result.returncode
    for width in (256,320):
        (out/f'{width}.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        frames={}
        for age in (118,130,132,140,160,220):
            folder,code=run(width,'neutral',age,save=age==140);frames['neutral',age]=folder
            checks[f'{width}_neutral{age}_exit']=code==0
            w,h,gold=pixels(component.parent/f'{width}-{age}.png');start=(320-width)//2;expected=[]
            for y in range(224):
                line=[c for x in range(start,start+width) for c in (gold[y*320+x],)*2];expected.extend(line);expected.extend(line)
            checks[f'{width}_neutral{age}_whole_client']=pixels(folder/'window.png')==(width*2,448,expected)
        for age in (140,150,151,159,160):
            folder,code=run(width,'no',age,save=age==150);frames['no',age]=folder
            checks[f'{width}_no{age}_exit']=code==0
            w,h,gold=pixels(oldbase/'no'/str(age)/'window.png')
            # Transport the original full320 client, then crop its centre.
            if width==256:
                gold=[gold[y*640+x] for y in range(448) for x in range(64,576)];picture=(512,448,gold)
            else:picture=(w,h,gold)
            checks[f'{width}_no{age}_whole_client']=pixels(folder/'window.png')==transport_window(picture,width)
        for age in (124,182,183,187,191,193,197,332,333,350,351):
            folder,code=run(width,'yes',age,save=age in (182,333));frames['yes',age]=folder
            checks[f'{width}_yes{age}_exit']=code==0
            original=oldbase/'yes'/f'{width}-124-{age}'/'window.png'
            checks[f'{width}_yes{age}_whole_client']=pixels(folder/'window.png')==transport_window(pixels(original),width)
        for kind,saved,target in (('neutral',140,160),('no',150,151),('yes',182,187),('yes',333,350)):
            cold,code=run(width,kind,target,label=f'cold{target}',load=frames[kind,saved]/'saved.state')
            checks[f'{width}_{kind}_cold{target}_exit']=code==0
            checks[f'{width}_{kind}_cold{target}_client']=pixels(cold/'window.png')==pixels(frames[kind,target]/'window.png')
            checks[f'{width}_{kind}_cold{target}_guest']=hashes(cold/'run.log')==hashes(frames[kind,target]/'run.log')
            checks[f'{width}_{kind}_cold{target}_pcm']=pcm(cold/'audio.wav')==pcm(frames[kind,target]/'audio.wav')[len(pcm(frames[kind,saved]/'audio.wav')):]
        for label,enabled,lle in (('native',False,False),('lle',True,True)):
            other,code=run(width,'yes',197,label=label,enabled=enabled,lle=lle)
            checks[f'{width}_{label}_exit']=code==0
            checks[f'{width}_{label}_guest']=hashes(other/'run.log')==hashes(frames['yes',197]/'run.log')
            checks[f'{width}_{label}_pcm']=pcm(other/'audio.wav')==pcm(frames['yes',197]/'audio.wav')
            if lle:checks[f'{width}_lle_client']=pixels(other/'window.png')==pixels(frames['yes',197]/'window.png')
        oldsave=oldbase/'continue'/f'{width}-140/saved.state'
        restored,code=run(width,'neutral',160,label='previous-save',load=oldsave)
        if width==256:
            checks['old256_layout_save_rejects_before_guest']=code==8 and b'loaded_state=' not in (restored/'run.log').read_bytes()
        else:
            checks['old320_layout_save_accepts']=code==0
            checks['old320_layout_save_picture']=pixels(restored/'window.png')==pixels(frames['neutral',160]/'window.png')
            checks['old320_layout_save_guest']=hashes(restored/'run.log')==hashes(frames['neutral',160]/'run.log')
    paths=[Path(__file__),build,*reports.values(),component,manifest,package,bank]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        comparison='Whole actual clients: independently transported previous verified canvases; no counter mask needed with preserved native count1',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
