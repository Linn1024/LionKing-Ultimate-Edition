"""Follow native submitted draw position pointers, as the compositor does."""
from pathlib import Path
template=Path(__file__).with_name('audit_cant_wait436_monkeys.py')
s=template.read_text().replace('build/cant-wait436-monkeys','build/cant-wait437-monkeys')
a=s.index('    for actor in range(');b=s.index('hashes={}',a)
s=s[:a]+'''    for draw in range(0x2000,0xffe0):
        pose=ptr(draw+10)
        if pose not in known:continue
        position=w(draw+4);actor=position-8
        if not 0x8000<=actor<=0xff80:continue
        live.append(dict(field=field,descriptor=hex(ptr(actor+4)),action=hex(ptr(actor+48)),pose=hex(pose),palette=(w(draw+8)>>9)&7,draw_owner=hex(w(actor+12)),draw=hex(draw)))
''' + s[b:]
s=s.replace('paths=[Path(__file__),reference]','paths=[Path(__file__),template,reference]')
exec(compile(s,str(template),'exec'))
