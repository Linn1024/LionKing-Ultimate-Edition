"""Build independent Hakuna/Destiny level and health-death music."""
from pathlib import Path
template=Path(__file__).with_name('build_next743.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard720/build-report.json'", "bp=ROOT/'build/hakuna829/build-report.json'").replace("out=ROOT/'build/next743'", "out=ROOT/'build/hakuna842'")
s=s.replace("('resources','audio','wide','sprites','assets','pride_data','roar','lizard')", "('resources','audio')")
a=s.index('db=json.loads(');b=s.index('for label,template,src,added in tasks:',a);s=s[:a]+s[b:]
exec(compile(s,str(template),'exec'))
