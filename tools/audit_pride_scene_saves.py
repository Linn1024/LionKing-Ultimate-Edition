"""Audit retained scene-save runs, including the expected old-player exit8."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch3';out=base/'scene-saves';build=bound(base/'build-report.json')
    checks={};count=0;pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for level in (1,10):
        for mode in ('aot','lle'):
            root=out/f'level{level}-{mode}';cold=root/'cold';state=root/'scene.state';data=state.read_bytes()
            flags=int.from_bytes(data[32:36],'little');rows=re.findall(pattern,(cold/'run.log').read_text())
            checks[f'{level}/{mode}/genuine_scene']=('Loading Monkeys' if level==1 else 'Loading Bug Toss') in (cold/'run.log').read_text()
            checks[f'{level}/{mode}/native_md_nonpride']=data[:8]==b'TLKSTAT1' and int.from_bytes(data[12:16],'little')==1600 and flags&0x20000000!=0 and flags&0x80000000==0
            checks[f'{level}/{mode}/cold_completed']=len(rows)==1800 and rows[-1][0]=='1800'
            for name in ('same-source','other-source'):
                folder=root/name;actual=re.findall(pattern,(folder/'run.log').read_text());audio=wav_data(folder/'audio.wav');count+=len(actual)
                checks[f'{level}/{mode}/{name}/all_fields']=actual==[r for r in rows if int(r[0])>1600] and len(actual)==200
                checks[f'{level}/{mode}/{name}/all_pcm']=bool(audio) and audio==wav_data(cold/'audio.wav')[-len(audio):]
                for what in ('guest','window'):checks[f'{level}/{mode}/{name}/{what}']=pixels(cold/(what+'.png'))==pixels(folder/(what+'.png'))
    oldlog=(out/'before/run.log').read_text()
    checks['old_failure_reproduced']='cannot save state' in oldlog and not (out/'old-scene.state').exists() and len(re.findall(pattern,oldlog))==1600
    paths=[Path(__file__),ROOT/'tools/verify_pride_scene_saves.py',base/'build-report.json',ROOT/'build/pride-launch2/build-report.json',ROOT/'profiles/pride-development-preview.ini',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,native_fields_compared=count,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='audit.json'},
                raw_runner_expected_failure='The final old-player run exited8 as expected; its helper asserted exit0 before report writing.',
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
