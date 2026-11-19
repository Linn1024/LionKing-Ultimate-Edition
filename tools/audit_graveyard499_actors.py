"""Normalize tagged 24-bit MD draw pointers when reading retained actor snapshots."""
from pathlib import Path
template=Path(__file__).with_name('audit_graveyard498_actors.py')
s=template.read_text().replace('build/graveyard498-actors','build/graveyard499-actors')
s=s.replace("s=s.replace(\"action=hex(long(actor))\", \"linked_neighbors=hex(long(actor))\")", "s=s.replace(\"action=hex(long(actor))\", \"linked_neighbors=hex(long(actor))\")\ns=s.replace('word(at)<<16|word(at+2)','(word(at)<<16|word(at+2))&0xffffff')\ns=s.replace('print(records,flush=True)',\"print('ORIGINAL_ACTORS',len(records),'UNIQUE_POSES',len(images),flush=True)\")")
exec(compile(s,str(template),'exec'))
