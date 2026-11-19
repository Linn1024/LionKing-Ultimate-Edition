"""Measure the real PCM15 tail to verify independent SNES-music playback."""
import array
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/md-continue-token-voice-duration';out.mkdir()
    source=ROOT/'tools/md_continue_token_voice_probe.c';sound=ROOT/'engine/runner/tlk_md_sound.c';sha=ROOT/'engine/snesrecomp/runner/src/sha256.c'
    exe=out/'probe.exe'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-std=c11','-static','-I'+str(ROOT/'engine/runner'),'-I'+str(sha.parent),str(source),str(sound),str(sha),'-lm','-o',str(exe)]
    subprocess.run(cmd,check=True,capture_output=True)
    backend=ROOT/'dist/installed-preview47/genesis_plus_gx_libretro.dll';shutil.copyfile(backend,out/backend.name)
    rom=ROOT/'Lion King, The (World).md'
    with (out/'run.log').open('wb') as log:rc=subprocess.run([str(exe),str(rom),str(out/'voice.pcm')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(rc,(out/'run.log').read_text())
    samples=array.array('h');samples.frombytes((out/'voice.pcm').read_bytes())
    peaks=[max(abs(v) for v in samples[n*1470:(n+1)*1470]) for n in range(240)]
    active=[n+1 for n,p in enumerate(peaks) if p>16]
    checks=dict(real_voice_audible=bool(active) and max(peaks)>1000,voice_finishes_within_fx_tail=bool(active) and active[-1]<120,silent_final_second=max(peaks[180:])<=16)
    paths=[Path(__file__),source,sound,sha,backend,rom]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,last_audible_60hz_block=active[-1] if active else None,peaks=peaks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,'last block',report['last_audible_60hz_block'],flush=True)


if __name__=='__main__':main()
