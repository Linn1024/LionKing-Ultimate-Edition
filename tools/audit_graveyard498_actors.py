"""Reuse retained sparse whole-route original RAM, without another game replay."""
from pathlib import Path
template=Path(__file__).with_name('audit_graveyard497_actors.py')
s=template.read_text().replace('build/graveyard497-actors','build/graveyard498-actors')
s=s.replace('for field in (14000,16000,18000):', "frames=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text());levels={r['frame']:r['level'] for r in frames}\nfor field in range(1,20000,100):\n    if levels.get(field)!=2:continue")
s=s.replace("path=ROOT/f'build/md-next-levels-replay/capture-{field}/work_ram.bin'", "path=ROOT/f'build/md-next-levels-replay/{field:05d}-wram.bin'")
s=s.replace("action=hex(long(actor))", "linked_neighbors=hex(long(actor))")
s=s.replace('paths=[Path(__file__)]',"paths=[Path(__file__),template,ROOT/'build/md-next-levels-replay/frames.json']")
exec(compile(s,str(template),'exec'))
