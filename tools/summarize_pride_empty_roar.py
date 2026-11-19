"""Bind current-value HUD ownership evidence; whole Pride/player remains open."""
import csv
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    evidence={}
    def sources(report):
        for name,sha in report.get('source_sha256',{}).items():assert digest(ROOT/name)==sha,name
    def load(key,path,expected='PASS'):
        path=ROOT/path;report=json.loads(path.read_text());assert report['result']==expected,(key,report['result'])
        sources(report)
        for name,sha in report.get('artifacts_sha256',{}).items():assert digest(path.parent/name)==sha,name
        evidence[key]=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=digest(path))
        return path,report
    _,oracle=load('current_font_cpu','build/pride-native-hud-current/report.json')
    assert oracle['original_roar_cases']==8436 and oracle['original_cpu_roar_font_bytes']==4319232
    assert oracle['transition_flags']==[0,1,3,65535] and oracle['original_cpu_execution']
    _,full=load('full_font_cpu','build/pride-native-hud-oracle/report.json')
    assert full['health_cases']==9 and full['roar_cases']==57
    _,control=load('native_controls','build/pride-empty-roar-controls/report.json')
    assert set(control['cases'])=={'320','256'}
    headless=ROOT/'engine/build-win/tlk_scene_prepared_probe.exe'
    sdl=ROOT/'engine/build-win/tlk_scene_prepared_sdl.exe'
    assert control['probe_sha256']==digest(headless)
    composed=clients=installed=transparent=duplicate_cases=0;guest=None;ram=None
    for width in (320,256):
        relative=f'build/pride-scene-render-prepared-headless-{width}-5400-checkpoint-both-roar-md/report.json'
        path,report=load(f'headless{width}',relative,'OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN')
        assert report['probe_sha256']==digest(headless) and report['revival_roar_source']=='md'
        assert report['checkpoint_sources']=='both' and report['prepared_objects']
        assert set(report['runs'])=={'native-owned','all-owned'}
        for name,run in report['runs'].items():
            folder=path.parent/name
            for filename,sha in run['artifacts_sha256'].items():assert digest(folder/filename)==sha,filename
            capture=json.loads((folder/'capture.json').read_text())
            assert capture['execution_completed'] and capture['probe_sha256']==digest(headless);sources(capture)
            assert run['release_age']==(347 if name=='native-owned' else 345)
            if guest is None:guest=run['guest'];ram=digest(folder/'route.ram')
            assert run['guest']==guest and digest(folder/'route.ram')==ram
            stages=list(csv.DictReader((folder/'prepared-objects.csv').open()))
            assert all(r['roar_current']=='0' for r in stages)
            assert {int(r['roar_initial_full']) for r in stages}<={0,3}
            composed+=run['pixels_compared']
        _,window=load(f'windows{width}',f'build/pride-scene-prepared-windows-{width}-checkpoint-both-roar-md/report.json')
        assert window['probe_sha256']==digest(sdl) and window['revival_roar_source']=='md'
        assert set(window['runs'])=={p+'-'+phase for p in ('native','all') for phase in ('display','revival','ready')}
        for name,run in window['runs'].items():
            assert run['actual_window_matches_owned_pixels']
            if name!='all-ready':assert run['identical_duplicate_presentations']>0
            duplicate_cases+=run['identical_duplicate_presentations']>0
            for filename,sha in run['artifacts_sha256'].items():
                assert digest(ROOT/f'build/pride-scene-prepared-windows-{width}-checkpoint-both-roar-md'/name/filename)==sha,filename
            clients+=run['exact_window_pixels']
        for host in ('headless','sdl'):
            _,font=load(f'fonts-{host}{width}',f'build/pride-checkpoint-player/empty-roar-fonts-{"sdl-" if host=="sdl" else ""}{width}.json')
            assert font['original_cpu_current_fonts_and_actual_owned_vram_exact']
            assert len(font['cases'])==(4 if host=='sdl' else 2)
            installed+=sum(r['actual_raster_indices'] for r in font['cases'].values())
            transparent+=sum(r['transparent_indices'] for r in font['cases'].values())
    _,counter=load('source_choice_counter','build/pride-revival-roar/report.json','AUDITED')
    assert counter['probe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_restore_probe.exe')
    assert counter['runs']['native']['previous_canonical_guest_and_full_tracked_ram_exact']
    assert counter['runs']['zero']['first_difference']==dict(age=352,actual=1,original_md=0)
    assert not counter['runs']['zero']['original_md_counter_sequence_exact']
    for name,run in counter['runs'].items():
        for filename,sha in run['artifacts_sha256'].items():assert digest(ROOT/'build/pride-revival-roar'/name/filename)==sha,filename
    _,clock=load('recovery_instruction_rule','build/pride-revival-roar-clock/report.json')
    assert clock['equal_low_clock_phase_rule_verified'] and not clock['absolute_cross_version_clock_phase_equivalence']
    production=json.loads((ROOT/'build/pride-checkpoint-player-latest.json').read_text())
    for name,sha in production['production_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(ROOT/'dist/LionKing.exe')==digest(ROOT/'engine/build-win/tlk_sdl.exe')
    result=dict(result='PARTIAL',scope=__doc__,headless_source_cases=4,actual_window_cases=12,
        whole_composed_pixels=composed,actual_client_pixels=clients,
        independent_installed_glyph_indices=installed,installed_transparent_indices=transparent,
        repeated_owned_presentation_cases=duplicate_cases,
        original_cpu_current_font_cases=8436,gameplay_source_independent_of_hud_artwork=True,
        last_actual_rebuild_context_preserved_across_cache_hits=True,
        default_full_roar_pixels_and_guest_ram_preserved=True,
        private_native_clock_phase_preserved=True,original_absolute_md_phase_verified=False,
        compiled_owner_verified=False,production_death_behavior_enabled=False,
        full_first_level_fidelity_complete=False,evidence=evidence,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        remaining=['Integrate/verify compiled ownership and independent public gameplay source',
                   'Verify clock lifecycle policy, default/final contexts, input/pause/reset/source changes and active saves',
                   'Complete source audio phase/policy, other widget/object semantics and full Pride fidelity checklist'])
    (ROOT/'build/pride-empty-roar-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Empty-roar ownership/font/window/control evidence bound: '+str(composed)+' composed pixels, '+
          str(clients)+' client pixels, '+str(installed)+' installed indices; full Pride PARTIAL',flush=True)


if __name__=='__main__':main()
