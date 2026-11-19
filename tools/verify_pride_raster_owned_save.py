"""Retain the actual practice-UI F1 record comparison on the raster candidate."""
from pathlib import Path
from audit_scenes import ROOT


if __name__=='__main__':
    source=(ROOT/'tools/verify_pride_overlay_owned_save.py').read_text()
    for old,new in {
        "base=ROOT/'build/pride-practice-live'":"base=ROOT/'build/pride-raster-state/live'",
        "paths=(Path(__file__),author_path":"paths=(Path(__file__),ROOT/'tools/verify_pride_overlay_owned_save.py',author_path",
    }.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
