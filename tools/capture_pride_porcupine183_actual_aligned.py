"""Ordinary difficulty routes with actual actor-ready timing observed, not assumed."""
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
plan_path=ROOT/'build/pride-porcupine182-actual-ready/report.json';plan=bound(plan_path);assert plan['result']=='PLANNED'
trim=plan['trim_fields'];assert 0<trim<400
verifier_source=Path(__file__).with_name('capture_pride_porcupine177_difficulty.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-porcupine177-difficulty'","ROOT/'build/pride-porcupine183-actual-aligned'")
anchor='prefix=prefix_path.read_bytes();start=len(prefix)//2';assert source.count(anchor)==1
source=source.replace(anchor,'prefix=prefix_path.read_bytes()[:-'+str(trim*2)+'];start=len(prefix)//2')
source=source.replace('TLK_CONTACT_FIRST166=str(start)','TLK_CONTACT_FIRST166=str(start-20)')
source=source.replace('dict(field=field,pad=pad,health=',"dict(field=field,pad=pad,scene=int.from_bytes(ram[0xdf:0xe2],'little'),health=")
anchor="assert rows and rows[0]['health']==4 and rows[0]['spares']==spares,(difficulty,rows[0])";assert source.count(anchor)==1
source=source.replace(anchor,"initial=next(r for r in rows if r['scene']==0xc00387 and r['health']==4 and r['player'][0]==64 and r['player'][1]>=1248)\n    assert initial['spares']==spares and start+1-initial['field']==14,(difficulty,initial,start)")
source=source.replace('dict(initial=rows[0],drops=drops','dict(initial=initial,drops=drops')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,plan_path,')
exec(compile(source,str(verifier_source),'exec'))
