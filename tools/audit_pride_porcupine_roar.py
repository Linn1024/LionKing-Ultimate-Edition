"""Bind real roar/attack interaction evidence and read-only observer neutrality."""
import csv
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-roar-bindings';out.mkdir();checks={}
    paths=[ROOT/'build/pride-porcupine-roar-qualification3/report.json',ROOT/'build/pride-porcupine-roar-saves/report.json',
           ROOT/'build/md-porcupine-roar3/report.json',ROOT/'build/md-porcupine-roar/report.json',
           ROOT/'build/md-porcupine-roar2/report.json',ROOT/'build/md-porcupine-roar-input/report.json',
           ROOT/'build/pride-porcupine-roar-qualification/report.json',ROOT/'build/pride-porcupine-roar-qualification2/report.json',
           ROOT/'build/pride-porcupine-roar-observer/build-report.json']
    qualification,saves,md,held,other,input_report,first,spaced,observer=[bound(p) for p in paths]
    checks['interaction60']=qualification['result']=='PASS' and len(qualification['checks'])==60 and all(qualification['checks'].values())
    checks['active_pulse_saves22']=saves['result']=='PASS' and len(saves['checks'])==22 and all(saves['checks'].values())
    checks['original_two_actual_pulses']=md['result']=='OBSERVED' and [md['cases'][k]['active_attack_observations'][0]['timer'] for k in ('roar32','roar48')]==['42','26']
    checks['original_countdowns_continue']=all(c['transitions'] and all(t['countdown_continues'] for t in c['transitions']) for k,c in md['cases'].items() if k in ('roar32','roar48'))
    checks['original_no_roar_reaction_during_attack']=not any(c['roar_reaction_calls'] for c in md['cases'].values())
    checks['original_held_through_turn_rejected']=not held['cases']['roar32']['active_attack_observations']
    raw=input_report['cases']['1'];edges=[r for r in raw if r['new']=='0x40']
    checks['actual_roar_edge_during_turn']=len(edges)==1 and edges[0]['action']=='0x192d32'
    checks['original_input_strength_available']=edges[0]['strength']>0
    checks['retained_other_button_probe']=other['result']=='NO_ACTIVE_ATTACK_ROAR'
    checks['retained_close_range_expectation']=first['result']=='FAIL' and len(first['checks'])==40 and sum(first['checks'].values())==38
    checks['retained_still_overlapping_expectation']=spaced['result']=='FAIL' and len(spaced['checks'])==56 and sum(spaced['checks'].values())==53
    source=ROOT/'build/pride-porcupine-roar-observer/contact-observer.c'
    reconstructed=source.read_text()
    for before,after in reversed(observer['replacements']):
        assert reconstructed.count(after)==1,after
        reconstructed=reconstructed.replace(after,before)
    checks['observer_only_logging_edits']=reconstructed==(ROOT/'engine/runner/tlk_porcupine_attack_runtime.c').read_text()
    checks['observer_binary_all321_inputs']=len(observer['link_inputs_sha256'])==321 and digest(source.parent/'player.exe')==observer['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in observer['link_inputs_sha256'].items())
    production_path=ROOT/'build/pride-porcupine38/build-report.json';production=bound(production_path);paths.append(production_path)
    a=production['link_inputs_sha256'];b=observer['link_inputs_sha256']
    checks['observer_one_object_only']=len(set(a)-set(b))==len(set(b)-set(a))==1 and all(a[p]==b[p] for p in set(a)&set(b))
    checks['production_unchanged']=digest(ROOT/'build/pride-porcupine38/player.exe')==production['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in a.items())
    base=ROOT/'build/pride-porcupine-roar-observer'
    for label,frame in [('roar-qualification-early-aot','1456'),('roar-late-opposite-aot','1472')]:
        p=base/label/'events.csv';paths.append(p)
        rows=list(csv.DictReader(p.open()));cues=[r for r in rows if r['event']=='0005' and r['descriptor']=='0387']
        checks[label+'_single_voice_at_activation']=[r['frame'] for r in cues]==[frame]
    for label in ('roar-qualification-held-turn-aot','roar-qualification-late-aot'):
        p=base/label/'events.csv';paths.append(p)
        checks[label+'_no_roar_voice']=not any(r['event']=='0005' and r['descriptor']=='0387' for r in csv.DictReader(p.open()))
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [Path(__file__),source,ROOT/'engine/runner/tlk_porcupine_attack_runtime.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        all_enemy_roar_or_ai_behaviors_proven=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
