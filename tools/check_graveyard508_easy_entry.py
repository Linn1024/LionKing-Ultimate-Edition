"""Use the already documented 30-frame Options adjustment debounce."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard507_easy_entry.py')
s=template.read_text().replace('build/graveyard507-easy-entry','build/graveyard508-easy-entry').replace("['A','wait 20']*2","['A','wait 30']*2")
s=s.replace("paths=[Path(__file__),helper,reference", "paths=[Path(__file__),template,ROOT/'engine/tools/make_play_tapes.py',helper,reference")
exec(compile(s,str(template),'exec'))
