"""Test source/build-bound prepared-bank records and atomic live application."""
import hashlib
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-native-bank/records';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    fixture=ROOT/'build/pride-native-bank/native-control'
    paths=[ROOT/'Lion King, The (USA).sfc',fixture/'capture-apu.bin',fixture/'capture-wram.bin',
           fixture/'before-apu.bin',fixture/'before-wram.bin']
    assert all(p.exists() for p in paths),'Run the ordinary component probe first'
    with (out/'build.log').open('wb') as log:
        subprocess.run(['cmake','--build','engine/build-win','--target','tlk_native_bank_test','-j','4'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    binary=ROOT/'engine/build-win/tlk_native_bank_test.exe'
    for mode in ('--write','--read'):
        with (out/(mode[2:]+'.log')).open('wb') as log:
            subprocess.run(list(map(str,[binary,*paths,mode,out/'bank.record',out/'continued-apu.bin'])),cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    logs={mode:(out/(mode+'.log')).read_text() for mode in ('write','read')}
    assert all('200000 SPC cycles/6250 new PCM frames, 0 failures' in log for log in logs.values())
    result={'result':'PASS','scope':__doc__,'test_sha256':digest(binary),'record_bytes':(out/'bank.record').stat().st_size,
        'new_process_continuation_spc_cycles':200000,'new_pcm_frames':6250,'queued_pcm_frames_preserved':37,
        'source_buffer_detachment':True,'source_build_and_semantic_record_guards':True,
        'failed_load_and_apply_preserve_live_state':True,'live_dsp_echo_ring_and_clocks_preserved':True,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in [Path(__file__),*paths,
            ROOT/'engine/tests/native_bank_test.c',ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/runner/tlk_native_bank.h']},
        'artifacts_sha256':{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='report.json'}}
    report.write_text(json.dumps(result,indent=2)+'\n')
    print('Prepared bank record/source/atomic guards and new-process 200000-cycle native PCM/echo continuation PASS',flush=True)


if __name__=='__main__':main()
