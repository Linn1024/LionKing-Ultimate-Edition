"""Audit completed UI restarts against an exact field-zero boot control.

--practice-level first consumes a discarded interval. Reuse the actual boot
save and original debug-menu input macro for the independent cold control.
Keep the earlier raw comparison, including its failed assumptions, intact.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_source_controls import macro_tape
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('music','start'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-soft-tree';build_path=base/'build-report.json';build=bound(build_path)
    root=base/'restarts'/args.case;raw_path=root/'report.json';raw=bound(raw_path)
    assert raw['result']=='INCOMPLETE' and raw['binary_sha256']==build['binary_sha256']
    failures={k for k,v in raw['checks'].items() if not v}
    assert failures==({'all_restarted_guest_fields','complete_restarted_pcm','all_restarted_audio_stems'} if args.case=='music' else {'all_restarted_guest_fields','complete_restarted_pcm'}),failures
    out=root/'boot-control';out.mkdir();live=root/'candidate'
    boot=live/'tlk_practice_boot.state';assert boot.read_bytes()[:8]==b'PRHBOOT1'
    tape=out/'level-select.raw';tape.write_bytes(macro_tape(bytes(6000)))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=live/'resources.ini';binary=base/'singlepass.exe';assert digest(binary)==build['binary_sha256']
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
         '--config',config,'--input-raw',tape,'--load',boot,'--frames','1800','--no-audio','--no-record','--no-pace',
         '--dump-png',out/'guest.png','--dump-window',out/'window.png','--wav',out/'audio.wav','--wav-seconds','100','--hash-at',','.join(map(str,range(1,1801)))]
    if args.case=='music':cmd+=['--lle']
    env=environment(out);env['TLK_START_TRACE']=str(out/'start.csv');env['TLK_MD_SOUND_COMMANDS']=str(out/'md-commands.csv');env['TLK_AUDIO_STEMS']=str(out/'audio-stems.csv')
    with (out/'run.log').open('wb') as log:r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert not r.returncode,r.returncode
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    a,b=rows(out),rows(live);fields=read_rows(live/'practice-fields.csv')
    cut=int(fields[-1800]['wav_frames_before_audio'])*4
    checks={k:v for k,v in raw['checks'].items() if k not in failures}
    checks['all_restarted_guest_fields']=len(a)==1800 and len(b)==3300 and a==b[-1800:]
    checks['complete_restarted_pcm']=wav_data(out/'audio.wav')==wav_data(live/'audio.wav')[cut:]
    stem=read_rows(out/'audio-stems.csv');actual=read_rows(live/'audio-stems.csv')
    checks['all_restarted_audio_stems']=bool(stem) and stem==actual[-len(stem):] if args.case=='music' else stem==actual==[]
    checks['final_cold_guest_picture']=pixels(out/'guest.png')==pixels(live/'guest.png')
    checks['actual_macro_from_field_zero']=len(read_rows(out/'practice-fields.csv'))==1800
    paths=[Path(__file__),raw_path,build_path,boot,profile,ROOT/'tools/verify_pride_source_controls.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=list(map(str,cmd)),binary_sha256=build['binary_sha256'],
                native_fields_compared=1800,pcm_rewind_byte_offset=cut,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
