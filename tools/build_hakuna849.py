"""Build noticeable Hakuna gorilla recovery, cub roar/effects and death movement."""
from pathlib import Path
template=Path(__file__).with_name('build_next743.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard720/build-report.json'", "bp=ROOT/'build/hakuna842/build-report.json'").replace("out=ROOT/'build/next743'", "out=ROOT/'build/hakuna849'")
s=s.replace("('resources','audio','wide','sprites','assets','pride_data','roar','lizard')", "('resources','audio','wide','roar')")
a=s.index('db=json.loads(');b=s.index('for label,template,src,added in tasks:',a);s=s[:a]+s[b:]
exec(compile(s,str(template),'exec'))
