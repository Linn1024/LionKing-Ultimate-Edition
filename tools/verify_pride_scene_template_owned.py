"""Preserve actual owned mixed-source revival and preceding-player saves."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_scene_template_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-scene-template-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    recipe=ROOT/'build/pride-launch2/probe/report.json';recipes=json.loads(recipe.read_text())
    cmd=recipes['commands']['md-death/after'];original=Path(cmd[cmd.index('--resource-profile')+1])
    out=base/'owned-regression';out.mkdir();profile=out/'mixed.ini';profile.write_bytes(original.read_bytes())
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';state=out/'preceding-owned-2001.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands={}
    def run(label,exe,mode,load=False,save=False):
        folder=out/label;folder.mkdir()
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profile,'--input',tape,'--frames',3000,
            '--hash-at',','.join(map(str,range(1,3001))),'--no-pace','--no-audio','--no-record',
            '--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        if save:command+=['--save-at','2001',str(state)]
        if load:command+=['--load',str(state)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        print(label,'complete',flush=True)
        return folder,re.findall(PATTERN,(folder/'run.log').read_text())
    old,reference=run('preceding-aot',public,'aot',save=True)
    state_sha=digest(state);whole=wav_data(old/'audio.wav')
    checks['preceding/owned_record']=state.read_bytes()[:8]==b'PRHSAVE1'
    checks['preceding/full_3000_guest_fields']=len(reference)==3000
    for mode in ('aot','lle'):
        label='candidate-'+mode;folder,rows=run(label,base/'player.exe',mode)
        checks[label+'/all_3000_guest_fields']=rows==reference
        checks[label+'/whole_mixed_pcm']=wav_data(folder/'audio.wav')==whole
        checks[label+'/whole_actual_client']=pixels(folder/'window.png')==pixels(old/'window.png')
        label='preceding-owned-load-'+mode;loaded,rows=run(label,base/'player.exe',mode,load=True)
        tail=wav_data(loaded/'audio.wav')
        checks[label+'/all_999_remaining_guest_fields']=len(rows)==999 and rows==reference[2001:]
        checks[label+'/entire_remaining_mixed_pcm']=bool(tail) and tail==whole[-len(tail):]
        checks[label+'/whole_actual_client']=pixels(loaded/'window.png')==pixels(old/'window.png')
        checks[label+'/preceding_save_unchanged']=digest(state)==state_sha
    paths=[Path(__file__),bp,public,recipe,original,tape,ROOT/'engine/runner/pride/pride_scene_template.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        existing_md_death_and_mixed_sources_preserved=True,new_death_capability=False,
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'owned/mixed/preceding-save checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
