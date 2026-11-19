"""Isolate94's actual wall-probe coordinate difference; never change production."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
wrapper=Path(__file__).with_name('audit_pride_hyena_walk_gate94.py')
script=wrapper.read_text()
anchor="exec(compile(source,str(verifier_source),'exec'))"
assert script.count(anchor)==1
injection='''
adjustments=[
    ("reference=ROOT/'build/pride-hyena-pounce-gate93/report.json'","reference=ROOT/'build/pride-hyena-walk-gate94/report.json'"),
    ("bound(reference)['result']=='POUNCE_GATES_VERIFIED'","bound(reference)['result']=='FAIL'"),
    ("out=ROOT/'build/pride-hyena-walk-gate94'","out=ROOT/'build/pride-hyena-walk-coordinates95'"),
    ('word(0x98ce+10,y);','word(0x98ce+10,y+8);'),
    ('equal=list(raw)==other','equal=list(raw[:5])+[raw[6]]==other[:5]+[other[6]]'),
    ('len(boundaries)*256*2**6','len(boundaries)*256*2**5'),
    ("result='WALK_GATES_VERIFIED'","result='WALK_COORDINATE_CAUSE_VERIFIED'"),
    ('Walking/turn decisions after earlier action gates; complete original wall queries on uniform synthetic 8x8 tile map and orientation writes. Stops before retreat action or final movement/animation. No whole AI/scene trajectory proof.',
     'Research alignment only: MD actorY is nativeY+8 so original wrapper probes use the same Y. Compare retreat/turn/facing/marker/render flip/retreat argument; retain raw platform-specific wall tags separately. This explains94 slope decisions, does not claim natural AI equivalence and changes no runtime.'),
    ('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/"tools/audit_pride_hyena_walk_gate94.py",'),
]
for before,after in adjustments:
    assert source.count(before)==1,before
    source=source.replace(before,after)
'''
script=script.replace(anchor,injection+'\n'+anchor)
exec(compile(script,str(wrapper),'exec'))
