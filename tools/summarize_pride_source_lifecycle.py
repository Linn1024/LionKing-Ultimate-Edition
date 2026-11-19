"""Bind exact music/start F12 lifecycles to the verified native raster candidate."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-source-live';paths=[Path(__file__)];reports={};checks=0;fields=0;pixels=0
    raster_path=ROOT/'build/pride-raster-state-latest.json';raster=bound(raster_path);paths.append(raster_path)
    assert raster['result']=='PARTIAL' and all(raster['checks'].values()) and not raster['pending_native_gates']
    build_path=ROOT/'build/pride-raster-state/build-report.json';build=bound(build_path);paths.append(build_path)
    identity=build['runs']['sdl']['binary_sha256']
    assert digest(ROOT/'build/pride-raster-state/live/runtime/practice-live.exe')==identity
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host in build['runs'].values():
        for name,sha in host['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for dirname,source_id in (('seeded','audio.music.pride_lands'),('start-fixed','gameplay.levels.pride_lands.start')):
        root=base/dirname;exact_path=root/'exact-report.json';r=bound(exact_path);paths.append(exact_path)
        assert r['result']=='PASS' and all(r['checks'].values()) and r['source_id']==source_id
        assert r['binary_sha256']==identity
        assert digest(ROOT/'build/pride-raster-state/live/runtime/genesis_plus_gx_libretro.dll')==r['dll_sha256']
        checks+=len(r['checks']);fields+=r['native_fields_compared'];pixels+=r['compared_final_client_pixels']
        reports[source_id]=digest(exact_path)
        for relative in ('report.json','controls/snes/report.json','controls/md/report.json'):
            path=root/relative;case=bound(path);paths.append(path)
            assert case['result']=='PASS' and all(case['checks'].values()) and case['binary_sha256']==identity
            checks+=len(case['checks'])
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,checks_passed=checks,
        actual_f12_source_changes=4,actual_f9_after_source_changes=2,source_leaf_ids=list(reports),
        every_native_video_and_wram_fields=fields,final_client_pixels_except_elapsed_run_value=pixels,
        whole_new_automatic_records_equal_to_cold_controls=4,all_four_pcm_segments_exact_per_case=True,
        cpu_mode='lle',viewport_width=320,graphics_profile='full supported MD graphics',
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        public_player_enabled=False,arbitrary_source_lifecycle_verified=False,mixed_ui_overlay_fidelity_complete=False,
        full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-source-lifecycle-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL music/start lifecycle:',checks,'checks;',fields,'native fields;',pixels,'scoped client pixels',flush=True)


if __name__=='__main__':main()
