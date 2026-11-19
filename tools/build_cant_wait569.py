"""Build corrected original ostrich animation-token addresses."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait565.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait560'", "base=ROOT/'build/cant-wait565'").replace("out=ROOT/'build/cant-wait565'", "out=ROOT/'build/cant-wait569'")
# The previous candidate already replaced the original roar object.
s=s.replace("rows=[x for x in db if", "rows=[x for x in db if")
a=s.index("rows=[x for x in db");b=s.index('tasks=',a)
s=s[:a]+s[b:];s=s.replace("argv(rows[0]['command'])","b['compiles']['roar']")
exec(compile(s,str(template),'exec'))
