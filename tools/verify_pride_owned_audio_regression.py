"""Preserve older routes with bounce native, then isolate repaired MD bounce."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-bounce-owner-work/player';bp=base/'build-report.json';bound(bp)
    public=ROOT/'build/pride-lizard-launch-work/player'
    public_report=public/'build-report.json';old=bound(public_report)
    assert digest(public/'player.exe')==old['binary_sha256']
    recipe=ROOT/'build/pride-launch2/probe/report.json';recipes=json.loads(recipe.read_text());assert recipes['result']=='PASS'
    out=base/'regression';out.mkdir();checks={};commands={};sources=[Path(__file__),bp,public_report,recipe]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(case,variant,cmd,profile):
        folder=out/(case+'-'+variant);folder.mkdir();cmd=list(cmd)
        cmd[0]=str(public/'player.exe' if variant=='public-native-bounce' else base/'player.exe')
        cmd[cmd.index('--resource-profile')+1]=str(profile)
        for flag,name in (('--config','host.ini'),('--wav','audio.wav'),('--dump-window','window.png'),('--dump-png','guest.png')):
            cmd[cmd.index(flag)+1]=str(folder/name)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        commands[folder.name]=cmd
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        rows=re.findall(pattern,(folder/'run.log').read_text())
        checks[folder.name+'/full_fields']=len(rows)==3000
        return rows,wav_data(folder/'audio.wav'),pixels(folder/'guest.png'),pixels(folder/'window.png')
    for case in ('native-aot','native-lle','mixed-native','md-death'):
        cmd=recipes['commands'][case+'/after'];original=Path(cmd[cmd.index('--resource-profile')+1]);sources.append(original)
        # Fresh controls remove the old volume mutation rather than bless its hashes.
        text=original.read_text();text=re.sub(r'^audio\.effects\.simba\.bounce\s*=.*$', '',text,flags=re.M)
        profile=out/(case+'-native-bounce.ini');profile.write_text(text+'\naudio.effects.simba.bounce = snes\n')
        previous=run(case,'public-native-bounce',cmd,profile)
        current=run(case,'candidate-native-bounce',cmd,profile)
        for index,field in enumerate(('every_guest_field','whole_pcm','guest_picture','actual_client')):
            checks[case+'/public_preserved_'+field]=previous[index]==current[index]
        if case in ('mixed-native','md-death'):
            selected=out/(case+'-md-bounce.ini');selected.write_text(text+'\naudio.effects.simba.bounce = md\n')
            changed=run(case,'candidate-md-bounce',cmd,selected)
            checks[case+'/bounce_preserves_guest_fields']=changed[0]==current[0]
            checks[case+'/bounce_preserves_guest_picture']=changed[2]==current[2]
            checks[case+'/bounce_preserves_actual_client']=changed[3]==current[3]
        print(case,'failed',[k for k,v in checks.items() if not v],flush=True)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope='four actual-public native-bounce controls; repaired toggle in mixed/death routes',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'regression checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
