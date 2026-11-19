"""Actual public-authored save and changed-source native-tail fallback."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound
from verify_pride_audio_state import wav_data,audio_offset


def main():
    public=ROOT/'build/pride-lizard-launch-work/player';base=ROOT/'build/pride-bounce-owner-work/player'
    current=base/'saves/native-aot-1400.state';assert current.is_file()
    bp=base/'build-report.json';bound(bp)
    oldbp=public/'build-report.json';old=bound(oldbp)
    assert digest(public/'native-engine/tlk_pride_player.exe')==old['binary_sha256']
    out=base/'legacy-source';out.mkdir();checks={};commands={}
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['SDL_VIDEODRIVER']='dummy'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(label,exe,profile,end,inputs,state=None,save=None,mode='aot'):
        folder=out/label;folder.mkdir()
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',public/'launch-audio/host.ini','--resource-profile',public/f'launch-audio/{profile}.ini',
            '--input-polled',inputs,'--frames',end,'--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,1501))),'--wav',folder/'audio.wav','--wav-seconds',100]))
        if mode=='lle':command+=['--lle']
        if state:command+=['--load',str(state)]
        if save:command+=['--save-at',str(end),str(save)]
        commands[label]=command
        local=dict(env,TLK_SEMANTIC_OWNER_TRACE=str(folder/'ownership.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=local,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        rows=re.findall(pattern,(folder/'run.log').read_text())
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        return folder,rows,wav_data(folder/'audio.wav'),sum(r['selector']=='2' and r['value']=='123' for r in driver)
    legacy=out/'actual-public-native-1400.state'
    folder,prefix_rows,prefix,_=run('public-author',public/'native-engine/tlk_pride_player.exe','native',1400,tape,save=legacy)
    raw=legacy.read_bytes();at=audio_offset(raw)
    checks['actual_public_authored_legacy_envelope']=raw[at:at+8]==b'TLKAUD01'
    reference=public/'bounce-semantic-prototype4/verification/native-aot'
    expected=re.findall(pattern,(reference/'run.log').read_text())
    checks['public_save_prefix_guest']=prefix_rows==expected[:1400]
    checks['public_save_prefix_pcm']=prefix==wav_data(reference/'audio.wav')[:len(prefix)]
    used=int(re.search(r'tape_words_used=(\d+)',(folder/'run.log').read_text()).group(1))
    suffix=out/'suffix.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
    runs={}
    for author,state in (('legacy',legacy),('current',current)):
        for profile in ('native','bounce'):
            for mode in ('aot','lle'):
                label=f'{author}-{profile}-{mode}'
                _,rows,pcm,count=run(label,base/'player.exe',profile,1500,suffix,state=state,mode=mode)
                checks[label+'/all_remaining_guest_fields']=rows==expected[1400:1500]
                checks[label+'/only_new_request_emits_md']=count==(1 if profile=='bounce' else 0)
                runs[label]=pcm
    for profile in ('native','bounce'):
        for mode in ('aot','lle'):
            checks[f'{profile}-{mode}/old_and_new_save_pcm']=runs[f'legacy-{profile}-{mode}']==runs[f'current-{profile}-{mode}']
        checks[profile+'/entire_mode_pcm']=runs[f'current-{profile}-aot']==runs[f'current-{profile}-lle']
    a,b=runs['current-native-aot'],runs['current-bounce-aot']
    checks['changed_source_preserves_initial_native_tail']=len(a)>40000 and a[:40000]==b[:40000]
    checks['new_md_bounce_audible_after_load']=a!=b
    sources=[Path(__file__),bp,oldbp,current,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        actual_legacy_author_sha256=old['binary_sha256'],remaining_fields_per_load=100,
        dummy_driver_only=True,prototype_only=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'legacy/source checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
