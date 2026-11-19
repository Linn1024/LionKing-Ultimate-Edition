"""Enable death-only MD presentation and validate its installed dependencies."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard684.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard659/build-report.json'", "bp=ROOT/'build/graveyard708/build-report.json'").replace("out=ROOT/'build/graveyard684'", "out=ROOT/'build/graveyard720'")
a=s.index('tasks=[');b=s.index('for label,template,src,added in tasks:',a)
s=s[:a]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c',False)]\n"+s[b:]
exec(compile(s,str(template),'exec'))
