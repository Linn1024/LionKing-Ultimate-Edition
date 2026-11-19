"""Compare new mixed-player cold execution against the preceding verified player."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=('native','md'),required=True);args=parser.parse_args()
    base=ROOT/'build/pride-cli-practice';case_path=base/args.case/'report.json';case=bound(case_path)
    assert case['result']=='PASS'
    old_build_path=ROOT/'build/pride-raster-state/build-report.json';old_build=bound(old_build_path)
    binary=ROOT/'build/pride-raster-state/live/runtime/practice-live.exe';assert digest(binary)==old_build['runs']['sdl']['binary_sha256']
    new_build_path=base/'build-report.json';new_build=bound(new_build_path)
    backend=binary.parent/'genesis_plus_gx_libretro.dll';assert digest(backend)==digest(base/backend.name)
    out=base/args.case/'prior';out.mkdir();author=base/args.case/'before/author'
    command=[str(binary)]+[v.replace(str(author),str(out)) for v in case['commands']['before/author'][1:]]
    config=out/'host.ini';config.write_bytes((author/'host.ini').read_bytes())
    env=environment(out);env.update(TLK_AUDIO_STEMS=str(out/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(out/'md-commands.csv'));env.pop('TLK_CLI_PRACTICE_LOG',None)
    with (out/'run.log').open('wb') as log:r=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    assert not r.returncode,r.returncode
    for path in out.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda f:re.findall(pattern,(f/'run.log').read_text())
    checks=dict(every_native_field=rows(out)==rows(author) and len(rows(out))==3000,
                complete_pcm=wav_data(out/'audio.wav')==wav_data(author/'audio.wav'),
                whole_client=pixels(out/'window.png')==pixels(author/'window.png'))
    names={'render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin','scenery-evidence.json'}
    artifacts=[p for p in author.rglob('*') if p.name in names]
    assert len([p for p in artifacts if p.name=='scenery-evidence.json'])>=2
    for path in artifacts:
        relative=path.relative_to(author);other=out/relative
        checks[str(relative).replace('\\','/')]=other.exists() and digest(other)==digest(path)
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    paths=[Path(__file__),case_path,old_build_path,new_build_path,backend,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS',checks=checks,command=command,binary_sha256=digest(binary),candidate_binary_sha256=new_build['runs']['before']['binary_sha256'],
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,'PASS prior player',len(checks),'checks',flush=True)


if __name__=='__main__':main()
