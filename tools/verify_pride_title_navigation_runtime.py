"""Qualify selected navigation against original outcomes, native controls and cold saves."""
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-title-navigation21';bound(base/'build-report.json')
    previous=ROOT/'build/pride-title-ready18';old=bound(previous/'verification/report.json')
    source=ROOT/'build/pride-title-navigation-edges2/report.json';original=bound(source)
    out=base/'verification';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    buttons={8:0x1000,16:0x800,32:0x400}
    def run(width,label,events,end=650,enabled=True,lle=False,save=False,load=None,old_player=False,expected_exit=0):
        folder=out/f'{width}-{label}';folder.mkdir();cmd=old['commands'][f'{width}-neutral'].copy()
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        if not old_player:cmd[0]=str(base/'player.exe')
        data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
        for at,md in events.items():
            held=sum(bit for mask,bit in buttons.items() if md&mask);struct.pack_into('<H',data,(4444+int(at)-1)*2,held)
        tape=folder/'input.tape';tape.write_bytes(data)
        if not old_player:
            profile=out/f'{width}-{"md" if enabled else "snes"}.ini'
            if not profile.exists():profile.write_text(Path(cmd[cmd.index('--resource-profile')+1]).read_text()+'\ngameplay.menus.title_navigation = '+('md' if enabled else 'snes')+'\n')
            cmd[cmd.index('--resource-profile')+1]=str(profile)
        for flag,value in [('--input',tape),('--frames',4444+end),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if lle:cmd.append('--lle')
        if save:cmd+=['--save-at',str(4444+end),str(folder/'saved.state')]
        if load:cmd[cmd.index('--load')+1]=str(load)
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1'),stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==expected_exit;print(folder.name,r.returncode,flush=True);return folder
    def same(label,a,b,skip=0):
        checks[label+'_client']=(a/'window.png').exists() and pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=(a/'audio.wav').exists() and pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for width in (256,320):
        controls={}
        for label in ('idle','selected','open','start515','start524'):
            events=original['observations'][label]['events']
            controls[label]=run(width,'control-'+label,events,enabled=False)
            legacy=run(width,'previous-'+label,events,old_player=True)
            same(f'{width}_{label}_native_unchanged',controls[label],legacy)
        live={}
        for label,row in original['observations'].items():
            live[label]=run(width,label,row['events'],save=label=='selected')
            expected=controls[row['outcome']]
            checks[f'{width}_{label}_original_visible_outcome']=pixels(live[label]/'window.png')==pixels(expected/'window.png')
            alternate=run(width,label+'-lle',row['events'],lle=True)
            same(f'{width}_{label}_lle',alternate,live[label])
        for age in (523,524,525):
            for case in ('selected-repeat524','selected-repeat525','held-start-into-ready','both-then-up524','both-then-down525'):
                row=original['observations'][case];saved=run(width,f'{case}-saved{age}',row['events'],end=age,save=True)
                cold=run(width,f'{case}-cold{age}',row['events'],load=saved/'saved.state')
                same(f'{width}_{case}_cold{age}',cold,live[case],len(pcm(saved/'audio.wav')))
                raw=(saved/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
                observations[saved.name]=dict(version=struct.unpack_from('<I',raw,at+8)[0],navigation=struct.unpack_from('<III',raw,at+180))
        raw=(live['selected']/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
        checks[f'{width}_saved_menu_v4']=struct.unpack_from('<I',raw,at+8)[0]==4
        checks[f'{width}_final_episode_retired']=struct.unpack_from('<I',raw,at+100)[0]==0
        rejected=run(width,'source-mismatch',{},load=live['selected']/'saved.state',enabled=False,expected_exit=8)
        log=(rejected/'run.log').read_text()
        checks[f'{width}_source_mismatch_before_guest']='loaded_state=' not in log and 'invalid' in log.lower()
    paths=[Path(__file__),base/'build-report.json',previous/'verification/report.json',source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
