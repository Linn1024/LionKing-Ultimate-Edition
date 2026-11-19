"""Confirm the current integrated nonfinal choice at ordinary fatal entry."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from verify_windows import pixels
from pride_bounce_owner_preview_history import bound


def main():
    out=ROOT/'build/pride-fatal-runtime';out.mkdir()
    exe=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(exe)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    results={};checks={};commands={}
    for choice in ('snes','md'):
        profile=out/(choice+'.ini')
        profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = '+choice+'\n')
        for mode in ('aot','lle'):
            label=choice+'-'+mode;folder=out/label;folder.mkdir()
            env=dict(clean,TLK_PRIDE_DIAGNOSTICS=str(folder))
            command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--config',config,'--resource-profile',profile,'--input-polled',tape,
                '--frames',4430,'--hash-at','4428,4429,4430','--no-pace','--no-audio','--no-record',
                '--dump-window',folder/'window.png']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            rows=re.findall(PATTERN,(folder/'run.log').read_text());checks[label+'/three_guest_samples']=len(rows)==3
            owner=folder/'owner-events.csv';events=list(csv.DictReader(owner.open())) if owner.exists() else []
            begin=[r for r in events if r['event']=='begin']
            checks[label+'/actual_source_guard']=len(begin)==1 if choice=='md' else not events
            if choice=='md':
                checks[label+'/native_fatal_marker_enters_owned_scene']=begin[0]['state']=='c35a82' and begin[0]['health']=='0' and begin[0]['field']=='4429'
            results[label]=dict(samples=rows,owner_begin=begin)
            print(label,'fatal entry complete',flush=True)
        checks[choice+'/mode_exact_guest_samples']=results[choice+'-aot']['samples']==results[choice+'-lle']['samples']
        checks[choice+'/mode_exact_real_client']=pixels(out/(choice+'-aot/window.png'))==pixels(out/(choice+'-lle/window.png'))
    checks['source_choices_match_predeath_sample']=results['snes-aot']['samples'][0]==results['md-aot']['samples'][0]
    paths=[Path(__file__),exe,tape,ROOT/'engine/runner/tlk_pride_launch.c',
        ROOT/'engine/cmake/game-patches/pride-health-death-resource.hunks',ROOT/'engine/cmake/TlkPrideCore.cmake']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,runs=results,commands=commands,
        current_nonfinal_md_death_revival_choice_is_integrated=True,
        sampled_fields=[4428,4429,4430],full_death_revival_reverified=False,
        fatal_hurt_body_emulation_added=False,production_changed=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'current fatal-entry checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
