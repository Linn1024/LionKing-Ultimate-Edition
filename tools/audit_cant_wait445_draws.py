"""Include all ROM pose banks when locating ostrich and giraffe draw ownership."""
from pathlib import Path
template=Path(__file__).with_name('audit_cant_wait444_animals.py')
s=template.read_text().replace('build/cant-wait444-animals','build/cant-wait445-draws').replace('0xc43000<=pose<0xc4b000','0xc00000<=pose<0xd00000')
s=s.replace('paths=[Path(__file__)]','paths=[Path(__file__),template]')
exec(compile(s,str(template),'exec'))
