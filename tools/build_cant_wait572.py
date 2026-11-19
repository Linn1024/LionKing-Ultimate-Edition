"""Build cub pickup voice correction; gameplay stays native."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait565.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait560'", "base=ROOT/'build/cant-wait569'").replace("out=ROOT/'build/cant-wait565'", "out=ROOT/'build/cant-wait572'")
a=s.index("rows=[x for x in db");b=s.index('tasks=',a)
s=s[:a]+s[b:];s=s.replace("argv(rows[0]['command'])","b['compiles']['roar']")
s=s.replace("'engine/runner/tlk_resources.c')", "'engine/runner/tlk_resources.c','engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks')")
exec(compile(s,str(template),'exec'))
