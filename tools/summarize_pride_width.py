"""Bind actual width/contact evidence and the isolated private-save I/O correction."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    old=ROOT/'build/pride-rng-player2';new=ROOT/'build/pride-rng-player3'
    paths=[Path(__file__)];new_checks=0;fields=0
    preceding=ROOT/'build/pride-rng-player-latest.json';prior=bound(preceding)
    assert prior['result']=='PARTIAL' and prior['checks']==129;paths.append(preceding)
    builds=[]
    for folder in (old,new,new/'width-observer'):
        p=folder/'build-report.json';r=bound(p);assert r['result']=='BUILT'
        assert digest(folder/'player.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in r.get('production_sha256',{}).items():assert digest(ROOT/name)==sha,name
        paths.append(p);builds.append(r)
    core=lambda r:{k:v for k,v in r['link_inputs_sha256'].items() if not k.endswith(('/host.obj','/temp-path.obj'))}
    assert core(builds[0])==core(builds[1])==core(builds[2])
    assert (new/'save-compatibility.json').read_bytes()==(old/'save-compatibility.json').read_bytes()
    paths.extend([new/'save-compatibility.json',ROOT/'engine/CMakeLists.txt'])
    def passing(path,count,nfields=0):
        nonlocal new_checks,fields
        r=bound(path);assert r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values()),path
        new_checks+=count;fields+=nfields;paths.append(path);return r
    passing(old/'width-contact-audit/report.json',8)
    passing(new/'concurrent-loads/report.json',35,400)
    race=passing(new/'shared-save-race/report.json',4)
    assert len(race['original_failures'])==4 and all(v['exit']==0 for v in race['cases']['new'].values())
    passing(new/'rng-private-slots/report.json',8,1711)
    passing(new/'completion-regression/report.json',10,12000)
    passing(new/'regression/report.json',20,12000)
    test_log=new/'concurrent-loads/test.log'
    assert test_log.read_text().strip()=='PASS 2215 temporary-path checks';paths.append(test_log)
    diagnostic=old/'width-diagnosis/report.json';d=bound(diagnostic)
    assert d['result']=='PASS' and d['observer_full_frame_wram_neutral_every_field'] and d['compared_fields']==3000
    assert d['observations']['first_player_difference']['field']==1403
    assert d['observations']['first_health_difference']['field']==1403
    paths.append(diagnostic);fields+=3000
    contact=old/'width-contact/report.json';c=bound(contact)
    assert c['result']=='CAPTURED' and c['observer_full_frame_wram_neutral_every_field'] and c['compared_fields']==2810
    paths.append(contact);fields+=2810
    control_cases=0
    for directory in ('width-controls','width-controls2'):
        p=old/directory/'report.json';r=bound(p);assert r['result']=='CAPTURED'
        assert r['ordinary_poweron_controller_inputs_only'] and not r['loaded_states'] and not r['guest_mutated']
        paths.append(p);control_cases+=len(r['cases'])
    assert control_cases==17
    for folder in (old/'width-jump8-route',old/'width-wait6-route',old/'width-wait12-route',new/'width-resync-route'):
        p=folder/'report.json';r=bound(p)
        assert r['result']=='CAPTURED' and r['observations']['level']==0 and r['observations']['first_next_level_field'] is None
        paths.append(p)
    authoring={}
    for name in ('width-plan3','width-plan4'):
        folder=new/name;p=folder/'report.json';r=bound(p)
        assert r['result']=='PARTIAL' and not r['waypoint_reached'] and not r['next_level_reached']
        assert r['uninterrupted_full_wram_matches_planning']
        assert r['headless_sha256']==builds[2]['binary_sha256']
        tape=folder/'best.polled.tape';assert digest(tape)==r['selected_tape_sha256']
        search_path=folder/'search.json';search=json.loads(search_path.read_text())
        chosen=ROOT/search['generations'][-1][0]['folder'];ram_name=f"wram-{r['final_frame']}.bin"
        assert (folder/'uninterrupted'/ram_name).read_bytes()==(chosen/ram_name).read_bytes()
        paths.extend([p,tape,search_path,folder/'uninterrupted'/ram_name,chosen/ram_name])
        authoring[name]=dict(final_frame=r['final_frame'],final=r['final'],waypoint_reached=False)
    preview=ROOT/'dist/development-preview/LionKing.exe'
    assert digest(preview)==digest(ROOT/'build/pride-launch2/player.exe');paths.append(preview)
    paths.extend([old/'width-contact-audit/256/window.png',old/'width-contact-audit/320/window.png',
                  new/'concurrent-loads/after-window/window.png',new/'rng-private-slots/live/client.png'])
    report=dict(result='PARTIAL',new_checks=new_checks,preceding_checks=129,helper_unit_checks=2215,
        compared_fields=fields,ordinary_control_cases=17,verified_authoring_prefixes=authoring,
        old_parallel_load_failures=4,new_parallel_load_failures=0,save_compatibility_unchanged=True,
        preceding_game_core_objects_unchanged=True,normal_rng_on_256_completion_verified=False,
        public_preview_unchanged=True,public_player_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=new/'width-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-width-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL',new_checks,'new checks;',fields,'compared fields; narrow route/full fidelity remain open',flush=True)


if __name__=='__main__':main()
