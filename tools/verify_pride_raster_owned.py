"""Retain second-revival cross-mode owned saves on the native raster backend."""
from pathlib import Path
from audit_scenes import ROOT

if __name__=='__main__':
    source=(ROOT/'tools/verify_pride_practice_owned.py').read_text()
    for old,new in {
        "base=ROOT/'build/pride-practice'":"base=ROOT/'build/pride-raster-state'",
        "binary=base/'practice-probe.exe'":"binary=base/'raster-probe.exe'",
        "Path(__file__),build_path":"Path(__file__),ROOT/'tools/verify_pride_practice_owned.py',build_path",
    }.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
