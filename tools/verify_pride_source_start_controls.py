"""Cold controls for initial-position switching with the actual constructor trace."""
from pathlib import Path
from audit_scenes import ROOT

if __name__=='__main__':
    source=(ROOT/'tools/verify_pride_source_controls.py').read_text()
    for old,new in {
        "env=environment(out);env['TLK_MD_SOUND_COMMANDS']":"env=environment(out);env['TLK_START_TRACE']=str(out/'start.csv');env['TLK_MD_SOUND_COMMANDS']",
        "paths=(Path(__file__),r_path":"paths=(Path(__file__),ROOT/'tools/verify_pride_source_controls.py',r_path",
    }.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
