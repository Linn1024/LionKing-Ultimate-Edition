"""Bind private checkpoint source/fade proofs; retain the MD roar-state gap."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    evidence={};pixels=head_pixels=cases=0
    binary=ROOT/'engine/build-win/tlk_scene_prepared_probe.exe'
    identity=digest(binary)
    def sources(report):
        for path,sha in report['source_sha256'].items():assert digest(ROOT/path)==sha,path
    for width in (320,256):
        for choice in ('native','frames','palette','both'):
            folder=ROOT/f'build/pride-scene-render-prepared-headless-{width}-5400-checkpoint-{choice}'
            path=folder/'report.json';report=json.loads(path.read_text())
            assert report['result']=='OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN'
            assert report['probe_sha256']==identity and report['checkpoint_sources']==choice
            assert report['prepared_objects'] and report['host']=='headless'
            sources(report)
            run=report['runs']['native-owned']
            assert run['black_reload_and_restore_verified'] and run['release_age']==347
            assert run['pixels_compared']==width*224*348
            assert run['md_base_palette_observed']==(choice in ('palette','both'))
            for name,sha in run['artifacts_sha256'].items():assert digest(folder/'native-owned'/name)==sha,name
            capture=json.loads((folder/'native-owned/capture.json').read_text())
            assert capture['execution_completed'] and capture['probe_sha256']==identity
            sources(capture)
            evidence[f'{width}-{choice}']=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=digest(path))
            pixels+=run['pixels_compared'];cases+=1
            if choice in ('palette','both'):
                path=ROOT/f'build/pride-checkpoint-player/private-checkpoint-{width}-{choice}-pixels.json'
                source=json.loads(path.read_text());assert source['result']=='PASS'
                sources(source)
                assert source['source_head_pixels']==51246 and len(source['fields'])==78
                evidence[f'{width}-{choice}-original-head']=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=digest(path))
                head_pixels+=source['source_head_pixels']
    for key,relative in (
        ('original_md_widget_counters','build/pride-checkpoint-player/md-restored-widget-counters/report.json'),
        ('original_md_widget_uploads','build/pride-checkpoint-player/md-restored-widgets/report.json')):
        path=ROOT/relative;report=json.loads(path.read_text());assert report['result']=='PASS'
        sources(report)
        evidence[key]=dict(path=relative,sha256=digest(path))
    assert report['original_uploaded_texture_indices']==232064 and report['restored_roar_current']==0
    assert report['native_canonical_roar_current']==24 and report['private_full_roar_source_semantics_divergence_open']
    result=dict(result='PARTIAL',scope=__doc__,probe_sha256=identity,headless_cases=cases,
        complete_composed_pixels_verified=pixels,original_md_checkpoint_base_pixels_verified=head_pixels,
        independent_checkpoint_frame_palette_choices=True,owned_unfaded_guard_and_semantic_fade=True,
        new_actual_windows_captured=False,production_death_behavior_enabled=False,
        original_md_roar_current_during_revival=0,private_native_roar_current_during_revival=24,
        full_first_level_fidelity_complete=False,evidence=evidence,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        remaining=[
            'Add independently selected original MD roar reset/recovery semantics; do not tie gameplay counter to HUD art',
            'Support and verify native partial/empty roar font generation when that gameplay source is selected',
            'Verify source widget/layout/priority semantics and new private actual Windows captures',
            'Complete compiled/default/final/input/lifecycle/save/audio/player integration and full Pride checklist'
        ])
    (ROOT/'build/pride-private-checkpoint-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Private8 source/width cases, '+str(pixels)+' complete pixels, '+str(head_pixels)+
          ' original head pixels bound; MD roar0 vs native24 divergence OPEN',flush=True)


if __name__=='__main__':main()
