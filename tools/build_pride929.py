"""Build independent adult-hyena/Simba/HUD and reviewed static object choices in7/8."""
from pathlib import Path
template=Path(__file__).with_name('build_next743.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard720/build-report.json'", "bp=ROOT/'build/later910/build-report.json'").replace("out=ROOT/'build/next743'", "out=ROOT/'build/pride929'")
s=s.replace("('resources','audio','wide','sprites','assets','pride_data','roar','lizard')", "('resources','audio','wide','sprites','assets','hitboxes')")
a=s.index('db=json.loads(');b=s.index('for label,template,src,added in tasks:',a);s=s[:a]+s[b:]
s=s.replace("for label,template,src,added in tasks:","tasks.append(('next_scene_data',b['compiles']['next_scene_data'],ROOT/'engine/runner/tlk_next_scene_data.c',False))\nfor label,template,src,added in tasks:")
exec(compile(s,str(template),'exec'))
