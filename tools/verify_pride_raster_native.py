"""Reuse plain-native early-state and actual-window gates for raster state."""
import argparse
from pathlib import Path
from audit_scenes import ROOT


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=('early','windows'),required=True);args=p.parse_args()
    tool='verify_pride_clock_early_state.py' if args.kind=='early' else 'verify_pride_clock_native_windows.py'
    source=(ROOT/'tools'/tool).read_text()
    for old,new in {
        "base=ROOT/'build/pride-restart-clock/native'":"base=ROOT/'build/pride-raster-state/native'",
        "Path(__file__),build_path":"Path(__file__),ROOT/'tools'/"+repr(tool)+",build_path",
    }.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
