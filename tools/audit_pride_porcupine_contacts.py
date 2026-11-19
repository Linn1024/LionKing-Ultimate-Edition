"""Bind real port/original contacts, pending input priority and hurt media."""
import csv
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    out=ROOT/'build/pride-porcupine-contact-bindings';out.mkdir();checks={}
    paths=[ROOT/'build/pride-porcupine-contact-verification2/report.json',
           ROOT/'build/pride-porcupine-contact-verification/report.json',
           ROOT/'build/md-porcupine-contact/report.json',ROOT/'build/md-porcupine-pending-jump/report.json',
           ROOT/'build/pride-porcupine-attack-evidence/report.json',ROOT/'build/md-porcupine-attack/report.json',
           ROOT/'tools/pride_npc_pairs.json']
    corrected,first,original,jump,native,md=[bound(p) for p in paths[:-1]]
    checks['contact_qualification59']=corrected['result']=='PASS' and len(corrected['checks'])==59 and all(corrected['checks'].values())
    checks['retained_cold_boundary_expectation_error']=first['result']=='FAIL' and len(first['checks'])==57 and sum(first['checks'].values())==56
    cases=original['cases']
    checks['four_original_md_damage_routes']=all(len(cases[name]['health_drops'])==1 and cases[name]['health_drops'][0]['before']==4 and cases[name]['health_drops'][0]['after']==3 for name in ('neutral','left4','left8','left16'))
    checks['original_md_first_phase28']=all(cases[name]['reactions'][0]['timer']=='28' and cases[name]['reactions'][0]['health']=='4' for name in ('left8','left16'))
    checks['original_md_actual_reaction_owner']=all(int(r['player_flags'],16)&4 and r['attacker']=='ff'+r['actor'] and r['victim']=='93ce' for name in ('neutral','left4','left8','left16') for r in cases[name]['reactions'])
    checks['original_md_one_update_damage_delay']=all(cases[name]['health_drops'][0]['field']==int(cases[name]['reactions'][0]['field'])+1 for name in ('neutral','left4','left8','left16'))
    checks['original_md_avoidance']=not cases['left32']['reactions'] and not cases['left32']['health_drops'] and cases['left32']['last_health']==4
    checks['original_md_jump_priority5']=jump['result']=='PASS' and len(jump['checks'])==5 and all(jump['checks'].values())
    base=ROOT/'build/pride-porcupine38'
    data=[json.loads(line) for line in (base/'contact-pending-jump/tree.jsonl').read_text().splitlines()]
    keyed={r['field']:r for r in data}
    checks['port_jump_polled_on_damage_update']=keyed[1472]['poll_index']==keyed[1471]['poll_index']+1 and keyed[1471]['health']==4 and keyed[1472]['health']==3
    for label in ('contact-hurt-view','contact-hurt-mixed','contact-hurt-mixed-lle','contact-mixed-tail','contact-mixed-tail-lle'):
        path=base/label/'report.json';paths.append(path);r=bound(path);checks[label+'_capture']=r['result']=='PASS'
    def equal(label,a,b):
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in ('window.png','scene.json','audio.wav','attack.csv','driver.csv'):checks[label+'_'+name]=digest(a/name)==digest(b/name)
    equal('hurt_media_modes',base/'contact-hurt-mixed',base/'contact-hurt-mixed-lle')
    equal('hurt_tail_modes',base/'contact-mixed-tail',base/'contact-mixed-tail-lle')
    a=json.loads((base/'contact-hurt-view/scene.json').read_text())
    b=json.loads((base/'contact-hurt-mixed/scene.json').read_text())
    checks['hurt_media_gameplay_independent']=a['latched_gameplay']==b['latched_gameplay'] and b['latched_gameplay']['health']==3
    checks['hurt_art_changes_client']=pixels(base/'contact-hurt-view/window.png')!=pixels(base/'contact-hurt-mixed/window.png')
    checks['hurt_sound_changes_pcm']=pcm(base/'contact-neutral-md/audio.wav')!=pcm(base/'contact-mixed-tail/audio.wav')
    driver=list(csv.DictReader((base/'contact-mixed-tail/driver.csv').open()))
    checks['hurt_md_pcm1_once_through_tail']=sum(r['selector']=='19' and r['value']=='1' for r in driver)==1
    for label in ('contact-hurt-view','contact-hurt-mixed'):
        rows=list(csv.DictReader((base/label/'events.csv').open()))
        checks[label+'_hurt_event1471_once']=[r['frame'] for r in rows if r['event']=='0012']==['1471']
    calls_path=ROOT/'build/md-porcupine-attack/calls.csv';paths.append(calls_path)
    rows=[r for r in csv.DictReader(calls_path.open()) if r['pc']=='19a446' and r['actor']=='98ce' and r['action']=='19a446']
    catalog={int(r['snes'],16):int(r['md'],16) for r in json.loads(paths[6].read_text())['pairs']}
    aligned=[]
    for sample in native['native_samples']:
        matches=[r for r in rows if int(r['timer'])==sample['timer'] and int(r['wait'])==sample['wait']]
        assert len(matches)==1,(sample,len(matches))
        r=matches[0]
        aligned.append(dict(native_field=sample['field'],md_field=int(r['field']),timer=sample['timer'],wait=sample['wait'],
            dx=sample['x']-int(r['x']),dy=sample['y']-int(r['y']),native_pose=sample['pose'],md_pose=r['pose'],
            pose_matches=catalog[int(sample['pose'],16)]==int(r['pose'],16)))
    checks['26_natural_phase_positions_match_translation']=len(aligned)==26 and {(r['dx'],r['dy']) for r in aligned}=={(66,1)}
    checks['26_natural_phase_poses_match']=all(r['pose_matches'] for r in aligned)
    build_path=base/'build-report.json';paths.append(build_path);build=bound(build_path)
    checks['production38_binary_inputs_unchanged']=digest(base/'player.exe')==build['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [Path(__file__),ROOT/'build/pride-porcupine-contact-media/mixed.ini',base/'contact-pending-jump/tree.jsonl']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,natural_alignment=aligned,
                full_enemy_physics_or_all_interruptions_proven=False,
                search_event_label_note='The exploratory hurt_events field holds0014, an enemy cue. Health loss and the original reaction/attacker link establish attribution; actual cub hurt event is0012.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
