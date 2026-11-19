"""Repeat only the compiled paths corrected after318; reuse unchanged controls."""
from pathlib import Path
template320=Path(__file__).with_name('verify_pride_battle318.py')
source=template320.read_text().replace("out=ROOT/'build/pride-battle318'","out=ROOT/'build/pride-battle320'").replace('pride-battle317','pride-battle319')
source=source.replace("commands={} ","commands={} ")
anchor="with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,['md-old','md-new','md-lle','native-old','native-new']))"
source=source.replace(anchor,"""import shutil
prior=json.loads((ROOT/'build/pride-battle318/report.json').read_text())
for label in ('md-old','md-lle','native-old'):
    shutil.copytree(ROOT/'build/pride-battle318'/label,out/label,dirs_exist_ok=True)
    commands[label]=prior['commands'][label]
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,['md-new','native-new']))
""")
source=source.replace("    commands[label]=cmd","    if label=='md-new':cmd+=['--save-at','3845',str(out/'current-battle.state')]\n    commands[label]=cmd")
source=source.replace('paths=[Path(__file__),build,reference]','paths=[Path(__file__),template320,build,reference,ROOT/\'build/pride-battle318/report.json\']')
exec(compile(source,str(template320),'exec'))
