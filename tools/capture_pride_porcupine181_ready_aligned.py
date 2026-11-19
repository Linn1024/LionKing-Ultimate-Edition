"""Shorten only the final neutral Options suffix to match observed gameplay age."""
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
plan_path=ROOT/'build/pride-porcupine180-ready/report.json';plan=bound(plan_path);assert plan['result']=='PLANNED'
trim=plan['trim_fields'];assert 0<trim<400
verifier_source=Path(__file__).with_name('capture_pride_porcupine177_difficulty.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-porcupine177-difficulty'","ROOT/'build/pride-porcupine181-ready-aligned'")
anchor='prefix=prefix_path.read_bytes();start=len(prefix)//2';assert source.count(anchor)==1
source=source.replace(anchor,'prefix=prefix_path.read_bytes()[:-'+str(trim*2)+'];start=len(prefix)//2')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,plan_path,')
exec(compile(source,str(verifier_source),'exec'))
