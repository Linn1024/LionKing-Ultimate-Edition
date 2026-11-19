"""Compare concurrent private loads, preceding cross-build saves and actual clients."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-rng-player3';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    previous=ROOT/'build/pride-rng-player2';out=base/'concurrent-loads';out.mkdir()
    state=previous/'width-plan2/anchor/end.state';initial_hash=digest(state)
    tape=previous/'width-plan2/d1-p0-L.polled.tape'
    profile=previous/'completion-reference-unpaused256/256/resources.ini'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};checks={}
    test_source=ROOT/'engine/tests/temp_path_test.c';test=out/'temp-path-test.exe'
    with (out/'test-compile.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-Wall','-Wextra','-Werror',
            '-I'+str(ROOT/'engine/runner'),str(test_source),str(ROOT/'engine/runner/tlk_temp_path.c'),'-o',str(test)],
            cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    result=subprocess.run([str(test)],cwd=ROOT,capture_output=True,check=True)
    (out/'test.log').write_bytes(result.stdout+result.stderr);print(result.stdout.decode().strip(),flush=True)
    checks['temporary_name_guards']=result.returncode==0
    def run(label,binary,mode,dummy=True,load=None,save=False):
        folder=out/label;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        env=dict(clean)
        if dummy:env['SDL_VIDEODRIVER']='dummy'
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--load',load or state,
             '--frames',1470 if not load else 1510,'--no-pace','--no-audio','--no-record',
             '--hash-at',','.join(map(str,range(1431 if not load else 1471,1471 if not load else 1511))),
             '--wav',folder/'audio.wav','--wav-seconds',120]
        if mode=='lle':cmd+=['--lle']
        if not dummy:cmd+=['--dump-window',folder/'window.png']
        if save:cmd+=['--save-at',1470,folder/'end.state']
        commands[label]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[label],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        return r.returncode
    checks['preceding_sequential_load']=run('before',previous/'player.exe','aot',save=True)==0
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs={i:pool.submit(run,f'after-{i}',base/'player.exe','aot' if i%2==0 else 'lle',save=True) for i in range(8)}
        results={i:f.result() for i,f in jobs.items()}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
    expected=rows('before');assert len(expected)==40
    for i,code in results.items():
        label=f'after-{i}';checks[label+'/load']=code==0
        checks[label+'/every_field']=len(rows(label))==40 and rows(label)==expected
        checks[label+'/whole_pcm']=wav_data(out/label/'audio.wav')==wav_data(out/'before/audio.wav')
    # Native inner state contains no temporary pathname. Both editor builds can
    # load each other's fresh private envelope under the unchanged contract.
    checks['forward_saved_load']=run('forward',base/'player.exe','aot',load=out/'before/end.state')==0
    checks['backward_saved_load']=run('backward',previous/'player.exe','aot',load=out/'after-0/end.state')==0
    checks['cross_build_every_field']=len(rows('forward'))==40 and rows('forward')==rows('backward')
    checks['cross_build_whole_pcm']=wav_data(out/'forward/audio.wav')==wav_data(out/'backward/audio.wav')
    checks['before_real_window']=run('before-window',previous/'player.exe','aot',dummy=False)==0
    checks['after_real_window']=run('after-window',base/'player.exe','lle',dummy=False)==0
    checks['whole_real_client']=pixels(out/'before-window/window.png')==pixels(out/'after-window/window.png')
    checks['original_save_preserved']=digest(state)==initial_hash
    checks['temporary_files_removed']=not list(state.parent.glob(state.name+'.*.practice-load.part'))
    paths=[Path(__file__),bp,previous/'build-report.json',state,tape,profile,test_source,ROOT/'engine/runner/tlk_temp_path.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        compared_fields=400,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())


if __name__=='__main__':main()
