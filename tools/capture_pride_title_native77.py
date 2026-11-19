"""Identify native title pictures at the frozen opening sound sequence."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    reference=ROOT/'build/pride-audio-dispatch75/report.json';prior=bound(reference)
    assert prior['result']=='CURRENT_DISPATCH_INVENTORIED'
    out=ROOT/'build/pride-title-native77';out.mkdir();checks={};commands={}
    expected=dict((int(f),(picture,ram)) for f,picture,ram in re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(reference.parent/'run.log').read_text()))
    def run(field):
        folder=out/str(field);folder.mkdir();cmd=prior['command'].copy()
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            old=Path(cmd[cmd.index(flag)+1]);(folder/file).write_bytes(old.read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        cmd[cmd.index('--frames')+1]=str(field);cmd[cmd.index('--hash-at')+1]=str(field)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        actual=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
        checks[str(field)+'_original_guest_endpoint']=actual==[(str(field),*expected[field])]
        with wave.open(str(folder/'audio.wav'),'rb') as sample,wave.open(str(reference.parent/'audio.wav'),'rb') as source:
            checks[str(field)+'_whole_pcm_prefix']=sample.readframes(sample.getnframes())==source.readframes(sample.getnframes())
        scene=json.loads((folder/'scene.json').read_text())
        commands[str(field)]=cmd
        print(field,'guest',checks[str(field)+'_original_guest_endpoint'],'pcm',checks[str(field)+'_whole_pcm_prefix'],'scene_level',scene['level'],flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,(600,630,730)))
    paths=[Path(__file__),reference,reference.parent/'run.log',reference.parent/'audio.wav',Path(prior['command'][0])]
    report=dict(result='NATIVE_TITLE_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                native_title_renderer_unchanged=True,original_md_equivalence_proven=False,production_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
