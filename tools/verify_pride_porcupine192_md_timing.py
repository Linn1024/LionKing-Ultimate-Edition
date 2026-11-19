"""Original damage/protection comparison with the MD attack-timing choice enabled."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_porcupine187_difficulty.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-porcupine186-polled/report.json'","ROOT/'build/pride-porcupine191-md-timing/report.json'").replace("ROOT/'build/pride-porcupine187-difficulty'","ROOT/'build/pride-porcupine192-md-timing'")
anchor="checks['source_hit_fields_not_equated']=True";assert source.count(anchor)==1
extra='''
control_path=ROOT/'build/pride-porcupine186-polled/report.json';control=bound(control_path);paths.append(control_path)
for difficulty in ('easy','normal','hard'):
    original_hit=control['cases'][difficulty]['porcupine_hits'][0]['field']
    selected_hit=native['cases'][difficulty]['porcupine_hits'][0]['field']
    checks[difficulty+'_actual_md_timing_hit14_fields_earlier']=original_hit-selected_hit==14
    trace=native_path.parent/difficulty/'attack.csv';calls=list(csv.DictReader(trace.open()));paths.append(trace)
    cues=[r for r in calls if r['pc']=='c15d14' and r['next']=='c15ca6']
    checks[difficulty+'_actual_md_cues_at28']=bool(cues) and all(r['timer']=='28' for r in cues)
    profile=native_path.parent/difficulty/'resources.ini';paths.append(profile)
    checks[difficulty+'_only_attack_timing_selected_md']=set(line.strip() for line in profile.read_text().splitlines() if line.strip())=={'schema = 1','game = snes','gameplay.levels.pride_lands.porcupine_attack = md'}
'''
source=source.replace(anchor,anchor+'\n'+extra)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
source=source.replace("scope='Attributed actual", "scope='Port porcupine attack timing selected MD; other resources SNES. Attributed actual")
exec(compile(source,str(verifier_source),'exec'))
