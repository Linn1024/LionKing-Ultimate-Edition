"""Use the actual F12 initial-position leaf with the same bounded restart probe."""
from pathlib import Path
from audit_scenes import ROOT

if __name__=='__main__':
    source=(ROOT/'tools/probe_pride_source_restart.py').read_text()
    for old,new in {
        "'audio.music.pride_lands = '":"'gameplay.levels.pride_lands.start = '",
        "click(154,267);click(154,295);click(174,324)":"click(154,267);click(154,324);click(174,436);click(194,464)\n                    USER32.PostMessageW(hwnd,0x200,0,300|(500<<16))\n                    USER32.PostMessageW(hwnd,0x20a,((-480)&65535)<<16,300|(500<<16));time.sleep(.4)",
        "click(575,352)":"click(575,295)",
        "click(490,405 if source=='snes' else 428)":"click(490,348 if source=='snes' else 371)",
        "wait(lambda:len(loads())>before_loads)":"deadline_before=until;until=min(until,time.monotonic()+6)\n                wait(lambda:len(loads())>before_loads)\n                until=deadline_before",
        "env=environment(folder);env['TLK_MD_SOUND_COMMANDS']":"env=environment(folder);env['TLK_START_TRACE']=str(folder/'start.csv');env['TLK_MD_SOUND_COMMANDS']",
        "paths=(Path(__file__),build_path":"paths=(Path(__file__),ROOT/'tools/probe_pride_source_restart.py',build_path",
    }.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
