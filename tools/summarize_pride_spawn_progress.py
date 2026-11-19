"""Index spawn-grid progress and the open completion regression without a green gate."""
import hashlib
import json
import re
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe';headless=ROOT/'engine/build-win/tlk_headless.exe'
    wanted={'pride-roll-verified/report.json':'PASS','pride-roll-contact-parity/report.json':'PASS',
            'pride-spawn-grid/report.json':'PASS','pride-checkpoint-revival/report.json':'PASS',
            'pride-mix-verification/report.json':'PASS','setup-verification/report.json':'PASS',
            'native-route-verification/play-report.json':'PASS','native-route-verification/allbugs-report.json':'PASS',
            'pride-spawn-initial/native.json':'PASS','pride-spawn-initial/md.json':'PASS',
            'pride-spawn-initial/compare.json':'DIFFERENCE','pride-roll-contacts/report.json':'PARTIAL',
            'pride-camera-completion-verified/report.json':'FAIL',
            'pride-camera-completion-verified/grid-failure-parity.json':'PASS'}
    reports={}
    for name,expected in wanted.items():
        path=ROOT/'build'/name;row=json.loads(path.read_text())
        assert row['result']==expected,(name,row['result'])
        assert path.stat().st_mtime>=player.stat().st_mtime,('Stale',name)
        if 'player_sha256' in row:assert row['player_sha256']==digest(player),name
        if 'headless_sha256' in row:assert row['headless_sha256']==digest(headless),name
        reports[name]={'result':expected,'sha256':digest(path)}
    for name,old in (('play-report.json','pride-spawn-native-before.json'),('allbugs-report.json','pride-spawn-allbugs-before.json')):
        now=json.loads((ROOT/'build/native-route-verification'/name).read_text())
        before=json.loads((ROOT/'build'/old).read_text());assert now['routes']==before['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/pride-spawn-allbugs-before.ram').read_bytes()
    manifest=json.loads((ROOT/'game-data/install.json').read_text());assert manifest['player_sha256']==digest(player)
    assert manifest['scene_cache']['sha256']=='94e6d05bad469ca7767ddd0878e2a5b057f379f99736744f471f89598d3c94d6'
    assert manifest['scene_cache']['version']==1 and manifest['scene_cache']['verified_background_levels']==[0,2]
    raw=(ROOT/'build/pride-spawn-mx.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    wrong=len(re.findall(r'^WRONG\b',log,re.M));unproven=len(re.findall(r'^UNPROVEN\b',log,re.M))
    assert wrong==0 and unproven==11
    report={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(headless),
            'reports':reports,'native_routes_unchanged':75,'allbugs_tracked_fields_unchanged':60648,
            'short_roll_protocols_matching':15,'short_roll_fields':2561,'common_short_roll_pose_counter_fields':475,
            'spawn_grid_actual_fields':1238,'spawn_grid_unique_original_cpu_fixtures':379,
            'long_contact_protocols_still_different':3,'long_contact_aot_lle_full_wram_fields':1238,
            'ordinary_checkpoint_health_death_and_mid_revival_save_verified_both_start_sources':True,
            'initial_enemy_spawn_order_matches_md':False,'authored_md_camera_completion_currently_passes':False,
            'installed_manifest_matches_player':True,'scene_cache':manifest['scene_cache'],
            'exit_mx':{'wrong':wrong,'existing_unproven':unproven,'full_proof':False},
            'full_first_level_fidelity_complete':False,
            'next':['Resolve independent initial enemy activation order and long contacts with original queue/lifecycle proof',
                    'Restore/adapt ordinary MD-camera completion; do not hide failing gate or disable source choices',
                    'Continue full Pride actor/enemy/effect/lifetime/collision/difficulty/audio/256 completion checklist']}
    path=ROOT/'build/pride-spawn-progress-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print('Spawn progress indexed as PARTIAL; authored MD-camera completion FAIL remains explicit:',path,flush=True)


if __name__=='__main__':main()
