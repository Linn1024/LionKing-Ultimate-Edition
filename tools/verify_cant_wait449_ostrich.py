"""Palette isolation during the ordinary power-on ostrich ride."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait441_monkeys.py')
s=template.read_text().replace('build/cant-wait440/build-report.json','build/cant-wait448/build-report.json').replace('build/cant-wait441-monkeys','build/cant-wait449-ostrich').replace('dist/installed-preview418','dist/installed-preview440')
s=s.replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.animals.ostriches.palette').replace('build/cant-wait437-monkeys/report.json','build/cant-wait447-ostrich/report.json')
s=s.replace("env={k:v", "for flag in ('--practice-level','--input'):\n    i=base.index(flag);del base[i:i+2]\nbase+=['--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape')]\nbase[base.index('--frames')+1]='7000';base[base.index('--hash-at')+1]='7000'\nenv={k:v")
s=s.replace('monkeys','ostriches').replace('monkey','ostrich')
s=s.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template,reference,')
exec(compile(s,str(template),'exec'))
