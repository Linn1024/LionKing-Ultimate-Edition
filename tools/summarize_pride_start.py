"""Index the initial-position milestone and explicit rolling gaps; Pride stays open."""
import hashlib
import json
import re
import subprocess
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe';headless=ROOT/'engine/build-win/tlk_headless.exe'
    runtime=('pride-start/report.json','pride-start-switch/report.json','pride-state-profiles/report.json',
             'pride-camera-completion-verified/report.json','pride-mix-verification/report.json',
             'pride-defeat-puff-art/report.json','pride-npc-verification/report.json',
             'pride-leaf-verification/report.json','pride-audio-state/report.json',
             'pride-presentation-state/report.json','presentation-schema-compat/report.json',
             'setup-verification/report.json','next-level-mix/report.json',
             'native-route-verification/play-report.json','native-route-verification/allbugs-report.json')
    reports={}
    for name in (*runtime,'pride-start-original/md.json','pride-start-original/native.json','pride-start-original/compare.json'):
        path=ROOT/'build'/name;row=json.loads(path.read_text())
        assert row['result']=='PASS',name
        if name in runtime:assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',name)
        reports[name]={'result':'PASS','sha256':digest(path)}
    for name,old in (('play-report.json','pride-start-native-before.json'),('allbugs-report.json','pride-start-allbugs-before.json')):
        a=json.loads((ROOT/'build/native-route-verification'/name).read_text())
        b=json.loads((ROOT/'build'/old).read_text());assert a['routes']==b['routes'],'Native final hashes changed'
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/pride-start-allbugs-before.ram').read_bytes()
    start=json.loads((ROOT/'build/pride-start/report.json').read_text())
    assert start['player_sha256']==digest(player) and start['headless_sha256']==digest(headless)
    save=ROOT/'build/pride-state-profiles/all-gameplay.state'
    assert int.from_bytes(save.read_bytes()[32:36],'little')&63==63
    manifest=json.loads((ROOT/'game-data/install.json').read_text());assert manifest['player_sha256']==digest(player)
    cache=manifest['scene_cache'];assert cache['version']==1 and cache['verified_background_levels']==[0,2]
    assert cache['sha256']=='94e6d05bad469ca7767ddd0878e2a5b057f379f99736744f471f89598d3c94d6'
    raw=(ROOT/'build/pride-start-mx.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    wrong=len(re.findall(r'^WRONG\b',log,re.M));unproven=len(re.findall(r'^UNPROVEN\b',log,re.M))
    assert wrong==0 and unproven==11
    roll_path=ROOT/'build/pride-roll-md-start/comparison.json';roll=json.loads(roll_path.read_text())
    assert roll['result']=='PARTIAL' and not roll['initial_spawn_offset_normalized'] and roll['md_start_selected']
    matched=[k for k,v in roll['cases'].items() if v['result']=='MATCH']
    gaps=[k for k,v in roll['cases'].items() if v['result']!='MATCH']
    assert len(matched)==13 and set(gaps)=={'right-roll-held','repeated-roll'}
    assert roll['paired_roll_pose_counter_fields']==455 and roll['total_fields_per_version']==2561
    units={}
    for name,extra in [('tlk_start_test',[]),('tlk_resources_test',[ROOT/'build/start-summary-unit.ini'])]:
        cmd=[ROOT/('engine/build-win/'+name+'.exe'),ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',*extra]
        result=subprocess.run(list(map(str,cmd)),cwd=ROOT,capture_output=True,text=True,check=True)
        assert 'PASS' in result.stdout;units[name]=result.stdout.strip()
    report={'result':'PASS','scope':__doc__,'resource_id':'gameplay.levels.pride_lands.start',
            'player_sha256':digest(player),'headless_sha256':digest(headless),'reports':reports,'units':units,
            'native_baselines_unchanged':True,'native_routes':75,'tracked_allbugs_fields':60648,
            'original_native_initial_xy':[64,1248],'original_md_initial_xy':[65,1255],
            'save_gameplay_source_bit':32,'all_six_gameplay_completion_verification_bound':5822,
            'source_aware_slots_and_actual_f12_restarts':True,'installed_manifest_matches_player':True,'scene_cache':cache,
            'rolling':{'result':'PARTIAL','report_sha256':digest(roll_path),'absolute_matching_protocols':matched,
                       'remaining_contact_damage_protocols':gaps,'common_roll_pose_counter_fields':455,'fields_per_version':2561},
            'exit_mx':{'wrong':wrong,'existing_unproven':unproven,'full_proof':False},
            'full_first_level_fidelity_complete':False,
            'remaining':['Actual checkpoint death/revival with selected initial-position source',
                         'Rolling contact/damage and enemy initialization/reactions/spawn/layout/collision/difficulty',
                         'Remaining actor/effect/particle/pickup/title states and active effect lifetime/removal',
                         'Remaining audio semantics and adapted256 ordinary completion; full Pride checklist']}
    path=ROOT/'build/pride-start-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print('Initial-position milestone and retained gates indexed; rolling gaps and full Pride scope stay open:',path,flush=True)


if __name__=='__main__':main()
