"""Run the same live F9 route with raster state and every-field native hashes."""
from pathlib import Path
from audit_scenes import ROOT


def main():
    source=(ROOT/'tools/verify_pride_live_restart.py').read_text()
    changes={
        "base=ROOT/'build/pride-practice-live'":"base=ROOT/'build/pride-raster-state/live'",
        "ROOT/'build/pride-overlay/build-report.json'":"ROOT/'build/pride-raster-state/build-report.json'",
        "ROOT/'build/pride-overlay/overlay-sdl.exe'":"ROOT/'build/pride-raster-state/raster-sdl.exe'",
        "('audio.effects = md\\n' if args.case=='md-media' else '')":"(''.join(line+'\\n' for line in (ROOT/'profiles/pride-lands.ini').read_text().splitlines() if line.startswith('audio.effects.') and line.endswith('= md')) if args.case=='md-media' else '')",
        "'--wav-seconds',200]":"'--wav-seconds',200,'--hash-at',','.join(map(str,range(1,3001)))]",
        "assert r.returncode==0,('baseline',r.returncode)":"assert r.returncode==0,('baseline',r.returncode)\n    assert 'Saved resource profile loaded' in (baseline/'run.log').read_text() and 'Profile rejected' not in (baseline/'run.log').read_text()",
        "paths=(Path(__file__),build_path":"paths=(Path(__file__),ROOT/'tools/verify_pride_live_restart.py',ROOT/'profiles/pride-lands.ini',build_path",
        "# F9 deliberately marks":"import re\n    pattern=r'frame=(\\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'\n    fields=[dict(field=n,frame=f,ram=w) for n,f,w in re.findall(pattern,(baseline/'run.log').read_text())]\n    actual=[dict(field=n,frame=f,ram=w) for n,f,w in re.findall(pattern,(live/'run.log').read_text())]\n    checks['all_native_video_fields_and_wram']=len(fields)==3000 and actual==project(fields)\n    # F9 deliberately marks",
    }
    for old,new in changes.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    # Keep this research driver source-bound without copying an independent
    # implementation of the existing actual-key lifecycle probe.
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))


if __name__=='__main__':main()
