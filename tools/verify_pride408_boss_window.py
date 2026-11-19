"""Capture inside the actual arena, before the route's later black transition."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride407_preset_window.py')
source=template.read_text().replace('build/pride407-preset-window','build/pride408-boss-window')
source=source.replace("i=cmd.index('--save-at');del cmd[i:i+3]", "i=cmd.index('--save-at');del cmd[i:i+3]\ncmd[cmd.index('--frames')+1]='3880';cmd[cmd.index('--hash-at')+1]='1500,2200'")
source=source.replace("if before['field']>=4400:", "if before['field']>=3650:")
source=source.replace("before=reader.snapshot()", "before=reader.snapshot();ram=reader.base+reader.symbols['_g_ram'];before['descriptor']=int.from_bytes(reader.read(ram+0xdf,3),'little');before['level']=int.from_bytes(reader.read(ram+0x1ff9e,2),'little')")
source=source.replace("after=reader.snapshot();break", "after=reader.snapshot();after['descriptor']=int.from_bytes(reader.read(ram+0xdf,3),'little');after['level']=int.from_bytes(reader.read(ram+0x1ff9e,2),'little');break")
source=source.replace("4400<=before['field']<=after['field']<4700", "3650<=before['field']<=after['field']<3894 and before['level']==after['level']==0 and before['descriptor']==after['descriptor']==0xc0080d and before['health']>0")
source=source.replace("rows(out/'run.log')==rows(reference.parent/'run.log')", "rows(out/'run.log')==[row for row in rows(reference.parent/'run.log') if row[0] in ('1500','2200')]")
start=source.index(",final_picture_equal=");end=source.index(",no_life_lost=",start)
source=source[:start]+",full_walkthrough_qualified=r['checks']['first_level_completed']"+source[end:]
source=source.replace("paths=[Path(__file__),reference,", "paths=[Path(__file__),template,reference,")
source=source.replace("One ordinary power-on full Available MD route in a real window, original boss-scene client inspected, next level reached with all8 spare lives. Same complete input/profile as406, selected guest samples/final client/PCM exact. No loaded states, guest edits, practice or unrelated source matrix.", "One actual Windows prefix with the exact406 Available MD profile/inputs. Capture is guarded to level0/arena C0080D before the later title/next-level black transition; selected prefix guest samples match406. Complete walkthrough/PCM remains qualified separately by406/407. No game fix or matrix.")
exec(compile(source,str(template),'exec'))
