"""Direct-selected rhino area, independent shared-tail palette isolation."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait441_monkeys.py')
s=template.read_text().replace('build/cant-wait440/build-report.json','build/cant-wait473/build-report.json').replace('build/cant-wait441-monkeys','build/cant-wait474-tail').replace('dist/installed-preview418','dist/installed-preview460')
s=s.replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.animals.rhinos.tail.palette').replace('build/cant-wait437-monkeys/report.json','build/cant-wait471-tail/report.json')
s=s.replace('env={k:v', "approach=json.loads((ROOT/'build/cant-wait462-rhino/report.json').read_text())['commands']['md']\nbase[base.index('--input')+1]=approach[approach.index('--input')+1]\nbase[base.index('--frames')+1]='1800';base[base.index('--hash-at')+1]='1800'\nenv={k:v")
s=s.replace('monkeys','tails').replace('monkey','tail').replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template,reference,')
exec(compile(s,str(template),'exec'))
