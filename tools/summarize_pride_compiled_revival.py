"""Bind current compiled revival evidence without claiming full scene support."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-compiled-revival';reports={}
    def read(name):
        path=base/name;value=json.loads(path.read_text())
        for source,sha in value.get('source_sha256',{}).items():assert digest(ROOT/source)==sha,source
        if 'script_sha256' in value:
            script='audit_pride_compiled_stack.py' if name.startswith(('sync-native-control/','sync-full-trace/')) else 'build_pride_compiled_sdl.py'
            assert digest(ROOT/'tools'/script)==value['script_sha256'],script
        reports[name]=digest(path);return value
    generation=read('generation-report.json');assert generation['result']=='GENERATED'
    assert generation['original_analysis_manifest_exact']
    for name,sha in generation['generated_sha256'].items():assert digest(base/'generated'/name)==sha,name
    build=read('build-report.json');assert build['result']=='BUILT'
    assert digest(base/'compiled-restore.exe')==build['binary_sha256']
    # The old builder inventories every object present in its output folder.
    # Validate the13 objects actually used by this headless link; an unrelated
    # private SDL host is subsequently rebuilt by the separate SDL tool.
    linked=[name+'.obj' for name in generation['instrumented_units']]+['private-host.obj']
    for name in linked:assert digest(base/'objects'/name)==build['object_sha256'][name],name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    sdl=read('sdl-build-report.json');assert sdl['result']=='BUILT'
    assert sdl['headless_build_report_sha256']==reports['build-report.json']
    assert digest(base/'compiled-restore-sdl.exe')==sdl['binary_sha256']
    assert digest(base/'objects/private-sdl-host.obj')==sdl['host_object_sha256']
    headless=read('sync-full-headless/report.json')
    assert headless['probe_sha256']==build['binary_sha256'] and headless['compiled_controller_trace_exact']
    assert headless['owner_events_exact'] and headless['restore_events_exact'] and headless['aot_and_lle_full_tracked_ram_exact']
    native=read('sync-native-control/report.json');trace=read('sync-full-trace/report.json')
    for report,key in ((native,'native'),(trace,'owned')):
        assert report['binary_sha256']==build['binary_sha256']
        assert not report['runs'][key]['full_wram_differences']
        assert not report['runs'][key]['low_wram_divergent_fields']
        assert report['runs'][key]['runs']['aot']['guest']==report['runs'][key]['runs']['lle']['guest']
    def hardware(path):
        result=[]
        for line in path.read_text().splitlines():
            words=line.split()
            if len(words)>2 and len(words[2])==4:
                int(words[2],16);result.append(words[:3])
        return result
    a=hardware(base/'sync-full-trace/owned-aot/hardware.log')
    b=hardware(base/'sync-full-trace/owned-lle/hardware.log');assert a and a==b
    total=0
    for width in (256,320):
        name=f'sync-windows-{width}/report.json';window=read(name)
        assert window['result']=='PASS' and window['binary_sha256']==sdl['binary_sha256']
        assert all(r['full_wram_exact'] and r['owner_and_restore_events_and_fields_exact'] for r in window['runs'].values())
        total+=window['real_client_pixels_exact']
    audio=read('sync-audio/report.json');assert audio['result']=='PASS'
    assert audio['binary_sha256']==sdl['binary_sha256'] and audio['pcm_exact'] and audio['guest_hashes_exact']
    assert audio['full_route_host_frames']==5400 and audio['full_route_duration_verified']
    # Verify frozen artifacts, not just the reports' positive booleans.
    for name in ('sync-full-headless/report.json','sync-native-control/report.json','sync-full-trace/report.json',
                 'sync-windows-256/report.json','sync-windows-320/report.json','sync-audio/report.json'):
        path=base/name;value=json.loads(path.read_text())
        for key,run in value['runs'].items():
            cases=run.get('runs',{key:run})
            for mode,case in cases.items():
                if name.startswith('sync-windows-'):folder=path.parent/(key+'-'+mode)
                elif name.startswith(('sync-native-control/','sync-full-trace/')):folder=path.parent/(key+'-'+mode)
                else:folder=path.parent/mode
                for artifact,sha in case['artifacts_sha256'].items():assert digest(folder/artifact)==sha,str(folder/artifact)
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        compiled_controller_and_bank_boundary_verified=True,full_route_low_wram_fields=trace['frames'],
        exact_hardware_touches=len(a),actual_windows_clients=12,exact_client_pixels=total,
        full_route_pcm_bytes=audio['pcm_bytes'],native_presenter_only=True,
        prepared_scene_presentation_verified=False,original_md_audio_phase_verified=False,
        active_scene_lifecycle_verified=False,production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-compiled-revival-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Compiled revival controller/bank/RAM/windows/PCM evidence bound; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
