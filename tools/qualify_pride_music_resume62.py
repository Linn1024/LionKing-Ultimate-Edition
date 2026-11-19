"""Resume current checkpoints with the remaining controller polls, not a replay restart."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_audio_state import wav_data


def main():
    source=ROOT/'build/pride-music-output62/verification/report.json';prior=bound(source)
    cursor_source=ROOT/'build/pride-music-transport59/verification/public-native/tree.jsonl'
    cursor=next(json.loads(line)['poll_index'] for line in cursor_source.read_text().splitlines() if json.loads(line)['field']==4000)
    out=source.parent/'resume-qualification';out.mkdir();checks={};commands={}
    checks['only_failed_original_checks_are_replay_suffix_checks']=all(v or any(part in k for part in ('resumed_guest','resumed_pcm','loaded_window','loaded_scene')) for k,v in prior['checks'].items())
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def run(name):
        folder=out/name;folder.mkdir();cmd=prior['commands'][name+'-loaded'].copy()
        tape=Path(cmd[cmd.index('--input-polled')+1]);(folder/'remaining.polled.tape').write_bytes(tape.read_bytes()[cursor*2:])
        cmd[cmd.index('--input-polled')+1]=str(folder/'remaining.polled.tape')
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        full=source.parent/name
        checks[name+'_exit']=rc==0
        checks[name+'_every600_resumed_guest_field_exact']=len(hashes(folder))==600 and hashes(folder)==[r for r in hashes(full) if int(r[0])>4000]
        whole=wav_data(full/'audio.wav');tail=wav_data(folder/'audio.wav')
        checks[name+'_whole_pcm_suffix_exact']=bool(tail) and whole[-len(tail):]==tail
        for file in ('window.png','scene.json'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(full/file)
        print(name,rc,flush=True)
    names=[choice+'-'+mode for choice in ('native','music') for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,names))
    for choice in ('native','music'):checks[choice+'_resumed_pcm_mode_parity']=digest(out/(choice+'-aot')/'audio.wav')==digest(out/(choice+'-lle')/'audio.wav')
    paths=[Path(__file__),source,cursor_source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,consumed_poll_words_at4000=cursor,
                same_build_checkpoints_only=True,original_failed_report_retained=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
