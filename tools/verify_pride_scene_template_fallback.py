"""Reproduce the public fallback crash, compare native execution and old saves."""
import argparse
import csv
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=ROOT/'build/pride-scene-template-work/player')
    args=parser.parse_args();base=args.base.resolve();bp=base/'build-report.json';build=bound(bp)
    candidate=base/'player.exe';assert digest(candidate)==build['binary_sha256']
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    out=base/'fallback';out.mkdir()
    tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
    assert not any(tape.read_bytes()[3421*2:]),'Loaded input suffix must remain neutral'
    zero=out/'neutral.polled.tape';zero.write_bytes(bytes(10000))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profiles={}
    for choice in ('snes','md'):
        profile=out/(choice+'.ini');profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = '+choice+'\n')
        profiles[choice]=profile
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands={};results={};state=out/'preceding-md-4800.state'
    def run(label,exe,choice,mode,expected=0,save=None,load=None):
        folder=out/label;folder.mkdir();end=5000
        env=dict(clean,TLK_PRIDE_DIAGNOSTICS=str(folder)) if choice=='md' and not load else dict(clean)
        env['TLK_TEMPLATE_PRESERVE']=str(folder/'templates.csv')
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profiles[choice],'--input-polled',zero if load else tape,
            '--frames',end,'--hash-at',','.join(map(str,range(1,end+1))),'--no-pace','--no-audio','--no-record',
            '--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        if save:command+=['--save-at','4800',str(save)]
        if load:command+=['--load',str(load)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            completed=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        checks[label+'/expected_exit']=completed.returncode==expected
        assert completed.returncode==expected,(label,completed.returncode)
        rows=re.findall(PATTERN,(folder/'run.log').read_text())
        results[label]=dict(exit_code=completed.returncode,fields=len(rows))
        print(label,'exit',completed.returncode,'sampled fields',len(rows),flush=True)
        return folder,rows
    native,reference=run('public-native-lle',public,'snes','lle')
    checks['native/all_5000_reference_fields']=len(reference)==5000
    old,failed=run('public-md-lle-fails',public,'md','lle',43,save=state)
    checks['public_crash/old_save_authored']=state.is_file()
    checks['public_crash/every_completed_field_matches_native']=len(failed)==4818 and failed==reference[:4818]
    state_sha=digest(state)
    whole=wav_data(native/'audio.wav')
    for choice,mode in (('snes','lle'),('md','aot'),('md','lle')):
        label='candidate-'+choice+'-'+mode;folder,rows=run(label,candidate,choice,mode)
        checks[label+'/all_5000_native_guest_fields']=rows==reference
        checks[label+'/entire_native_pcm']=wav_data(folder/'audio.wav')==whole
        checks[label+'/actual_native_client']=pixels(folder/'window.png')==pixels(native/'window.png')
        if choice=='md':
            checks[label+'/unowned_reload_remains_native']=not any(',prepared,' in line for line in (folder/'decompress.csv').read_text().splitlines())
            checks[label+'/repeat_recipe_passes_fault_boundary']='4819,0,c1cd75,ee6e03' in (folder/'decompress.csv').read_text()
            if (folder/'templates.csv').exists():
                capsules=list(csv.DictReader((folder/'templates.csv').open()))
                checks[label+'/all_7_capsules_unchanged_across_native_redecode']=len(capsules)==14 and all(r['unchanged']=='1' for r in capsules)
    for mode in ('aot','lle'):
        label='preceding-save-'+mode;folder,rows=run(label,candidate,'md',mode,load=state)
        tail=wav_data(folder/'audio.wav')
        checks[label+'/all_200_remaining_native_guest_fields']=len(rows)==200 and rows==reference[4800:]
        checks[label+'/entire_remaining_native_pcm']=bool(tail) and tail==whole[-len(tail):]
        checks[label+'/whole_final_client']=pixels(folder/'window.png')==pixels(native/'window.png')
        checks[label+'/preceding_save_unchanged']=digest(state)==state_sha
    paths=[Path(__file__),bp,public,tape,ROOT/'engine/runner/pride/pride_scene_template.h',ROOT/'build/pride-scene-template-baseline/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,runs=results,
        public_failure_exit=43,first_uncaptured_field=4819,
        native_fallback_preserved=True,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'fallback/save checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
