"""Capture actual paced audio-device playback at the corrected title boundary."""
import json
import os
from pathlib import Path
import re
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-title-ready18';source=base/'verification/report.json';old=bound(source)
    out=base/'device';out.mkdir();cmd=old['commands']['320-menu515'].copy()
    for flag in ('--no-audio','--no-pace'):cmd.remove(flag)
    for flag,value in [('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json'),('--wav',out/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    with (out/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    reference=source.parent/'320-menu515';a=pcm(out/'audio.wav');b=pcm(reference/'audio.wav')
    text=(base/'frontend/sdl_main.c').read_text();log=(out/'run.log').read_text()
    counters=re.search(r'audio_underruns=(\d+) late_resyncs=(\d+)',log)
    checks=dict(exit=r.returncode==0,client=pixels(out/'window.png')==pixels(reference/'window.png'),guest=hashes(out/'run.log')==hashes(reference/'run.log'),
                adaptive_budget_source='want *= 1.0 + 0.005 * e;' in text and 'SDL_GetAudioStreamQueued(astream)' in text,
                samples_within_servo=abs(len(a)-len(b))<=len(b)*.005+8,recorded_sound=any(a) and any(b),
                no_audio_fallback='continuing without sound' not in log and counters is not None)
    observations=dict(device_samples=len(a)//4,offline_samples=len(b)//4,underruns=int(counters[1]) if counters else None,
                      late_resyncs=int(counters[2]) if counters else None,strict_device_offline_pcm_equality_claimed=False)
    paths=[Path(__file__),source,base/'frontend/sdl_main.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),observations,flush=True)


if __name__=='__main__':main()
