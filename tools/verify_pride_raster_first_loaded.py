"""First/eighth loaded mixed clients and audio with the native raster record."""
from pathlib import Path
from audit_scenes import ROOT


if __name__=='__main__':
    source=(ROOT/'tools/verify_pride_practice_first_loaded.py').read_text()
    replacements={
        "base=ROOT/'build/pride-practice'":"base=ROOT/'build/pride-raster-state'",
        "author=base/'verified/normal-ui'/name":"author=base/'live'/('md-media' if args.case=='md' else 'native')",
        "state=author/'automatic-original.state';saved=r['observations']['automatic_saved_field']":"state=author/'baseline/tlk_practice_restart.state';saved=r['saved_field']",
        "binary=base/'practice-sdl.exe'":"binary=base/'live/runtime/practice-live.exe'",
        "paths=(Path(__file__),build_path":"paths=(Path(__file__),ROOT/'tools/verify_pride_practice_first_loaded.py',build_path",
    }
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
