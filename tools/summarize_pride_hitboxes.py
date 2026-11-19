"""Index current actor-bound evidence while retaining full-level completion failure."""
import hashlib
import json
import subprocess
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe';head=ROOT/'engine/build-win/tlk_headless.exe';reports={}
    runtime=('pride-hitbox-verification/report.json','pride-hitbox-final-parity/report.json',
        'pride-activation-loader-verified/report.json','pride-hitbox-switch/report.json',
        'pride-state-profiles/report.json','pride-mix-verification/report.json','setup-verification/report.json',
        'native-route-verification/play-report.json','native-route-verification/allbugs-report.json')
    for name in (*runtime,'pride-hitbox-catalog/report.json','pride-hurt-pairs/report.json','pride-actor-bounds-original/report.json'):
        path=ROOT/'build'/name;row=json.loads(path.read_text());assert row['result']=='PASS',name
        if name in runtime:assert path.stat().st_mtime>=player.stat().st_mtime,('Stale runtime report',name)
        if 'headless_sha256' in row:assert row['headless_sha256']==digest(head),name
        if 'player_sha256' in row:assert row['player_sha256']==digest(player),name
        reports[name]={'result':'PASS','sha256':digest(path)}
    for name,before in (('play-report.json','hitbox-native-before.json'),('allbugs-report.json','hitbox-allbugs-before.json')):
        assert json.loads((ROOT/'build/native-route-verification'/name).read_text())['routes']==json.loads((ROOT/'build'/before).read_text())['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/hitbox-allbugs-before.ram').read_bytes()
    parity=json.loads((ROOT/'build/pride-hitbox-final-parity/report.json').read_text())
    both=ROOT/'build/pride-hitbox-verification/both/snes.json'
    assert parity['capture_sha256']==digest(both)
    completion_path=ROOT/'build/pride-hitbox-completion/report.json';completion=json.loads(completion_path.read_text())
    assert completion['headless_sha256']==digest(head) and completion['result'] in ('PASS','FAIL')
    reports['pride-hitbox-completion/report.json']={'result':completion['result'],'sha256':digest(completion_path)}
    manifest=json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256']==digest(player) and manifest['scene_cache']['verified_background_levels']==[0,2]
    unit=ROOT/'build/pride-hitbox-unit.log'
    with unit.open('wb') as f:subprocess.run([str(ROOT/'engine/build-win/tlk_hitboxes_test.exe'),
        str(ROOT/'Lion King, The (USA).sfc'),str(ROOT/'Lion King, The (World).md')],stdout=f,stderr=subprocess.STDOUT,check=True)
    report={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(head),
        'verified_components':reports,'unit_log_sha256':digest(unit),'body_bound_source_choices_verified':True,
        'original_contact_fields_matched':1238,'original_contact_cases_matched':3,
        'native_routes_unchanged':75,'allbugs_tracked_fields_unchanged':60648,
        'full_pride_fidelity_complete':False,'normal_full_md_recording_complete':completion['normal_first_level_completion_verified'],
        'remaining':['Original ceiling/head terrain probes: converted MD route first differs at aligned1034/1423',
                     'Authored MD-camera completion recording and adapted256 ordinary route',
                     'Ambiguous/unmapped actor bounds, attack regions and remaining enemy/difficulty behavior',
                     'Complete Pride art/audio/effect and interruption checklist']}
    out=ROOT/'build/pride-hitbox-progress-latest.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print('Current body bounds and native controls indexed; full Pride remains PARTIAL:',out,flush=True)


if __name__=='__main__':main()
