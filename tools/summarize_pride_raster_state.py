"""Bind the raster failure, repair, actual F9/audio/UI-save and native gates."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import read_rows
from verify_pride_audio_state import wav_data
from verify_windows import hashes, pixels


def main():
    base=ROOT/'build/pride-raster-state';build_path=base/'build-report.json';build=bound(build_path)
    native_path=base/'native/build-report.json';native=bound(native_path)
    paths=[Path(__file__),build_path,native_path];reports={};checks={};passed=0;video_fields=0;client_pixels=0
    for report,folder,stem in ((build,base,'raster-'),(native,base/'native','native-')):
        for name,sha in report['production_sha256'].items():assert digest(ROOT/name)==sha,name
        for host,r in report['runs'].items():
            assert digest(folder/(stem+host+'.exe'))==r['binary_sha256']
            for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    old_path=ROOT/'build/pride-practice-live/native/report.json';old=bound(old_path);paths.append(old_path)
    assert old['result']=='INCOMPLETE'
    assert {k for k,v in old['checks'].items() if not v}=={'second-prefix/render-owned.rgb','second-prefix/render-fields.csv'}
    diagnostic_path=ROOT/'build/pride-practice-live/native-diagnostic/report.json';diagnostic=bound(diagnostic_path);paths.append(diagnostic_path)
    checks['reproduced_native_video_without_mixed_renderer']=diagnostic['exit_code']==0 and diagnostic['private_mixed_renderer_enabled'] is False and len(diagnostic['comparisons'][0]['differences'])==286 and all(d['frame_diff'] and not d['ram_diff'] for d in diagnostic['comparisons'][0]['differences'])
    for name in ('native','md-media'):
        path=base/'live'/name/'report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values()),name
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']==digest(base/'live/runtime/practice-live.exe')
        assert r['dll_sha256']==digest(base/'live/runtime/genesis_plus_gx_libretro.dll')
        reports[name]=digest(path);passed+=len(r['checks']);client_pixels+=r['compared_client_pixels']
        video_fields+=len(read_rows(path.parent/'live/practice-fields.csv'))
        checks[name+'-every-native-video-and-wram-field']=r['checks']['all_native_video_fields_and_wram']
        checks[name+'-actual-f9-owned']=len(r['observed_loads'])==2 and r['checks']['first_owned'] and r['checks']['second_owned']
        if name=='md-media':
            checks['selected-md-payload']=r['md_audio_selected'] and r['md_audio_payload_bytes']>0
            stems=read_rows(path.parent/'baseline/audio-stems.csv')
            checks['audible-md-stem']=max(int(row['md_peak']) for row in stems)>0
            commands=read_rows(path.parent/'baseline/md-commands.csv')
            checks['md-effect-commands']=any(row['selector']=='2' for row in commands)
        audit_path=base/'live/owned-ui-save-audit'/name/'report.json';audit=bound(audit_path);paths.append(audit_path)
        preceding=base/'live/owned-ui-save'/name/'report.json';bound(preceding);paths.append(preceding)
        assert audit['result']=='PASS' and all(audit['checks'].values())
        assert audit['binary_sha256']==r['binary_sha256'] and audit['dll_sha256']==r['dll_sha256']
        reports[name+'-owned-ui-save']=digest(audit_path);passed+=len(audit['checks'])
    # Saving the raster data must leave the uninterrupted native run alone.
    before=ROOT/'build/pride-practice-live/native/baseline';after=base/'live/native/baseline'
    checks['uninterrupted-previous-guest']=hashes(before/'run.log')==hashes(after/'run.log')
    checks['uninterrupted-previous-client']=pixels(before/'window.png')==pixels(after/'window.png')
    checks['uninterrupted-previous-pcm']=wav_data(before/'audio.wav')==wav_data(after/'audio.wav')
    for name in ('render-owned.rgb','prepared-fonts.bin','prepared-objects.csv'):
        checks['uninterrupted-previous-'+name]=digest(before/name)==digest(after/name)
    for name in ('backend-native','crc-md'):
        path=base/'verified/rejection'/name/'report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values()),name
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        raw=(path.parent/'candidate/tlk_slot1.state').read_bytes()
        import struct
        blob_start=256+36;blob_end=blob_start+struct.unpack_from('<Q',raw,256+24)[0]
        marker=raw.rfind(b'PPRJ',blob_start,blob_end)
        checks[name+'-bad-raster-cursor']=marker>=blob_start and struct.unpack_from('<I',raw,marker+8)[0]==2
        reports[name+'-raster-rejection']=digest(path);passed+=len(r['checks'])
    first_loaded_pixels=0
    for name in ('native','md'):
        path=base/'verified/first-loaded'/name/'report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values()),name
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        reports[name+'-first-loaded']=digest(path);passed+=len(r['checks']);first_loaded_pixels+=r['pixels_compared']
    for name in ('0','1'):
        path=base/'verified/owned-saves'/name/'report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values())
        assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
        reports[name+'-headless-owned']=digest(path);passed+=len(r['checks'])
    owned_window_pixels=0;owned_window_fields=0
    for name in ('native','md-media'):
        path=base/'verified/windows-owned-audit'/name/'report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values())
        prior_path=base/'verified/windows-owned'/name/'report.json';prior=bound(prior_path);paths.append(prior_path)
        assert prior['result']=='INCOMPLETE' and {k for k,v in prior['checks'].items() if not v}=={'bank-clock.csv'}
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        reports[name+'-windows-owned-audit']=digest(path)
        passed+=len(r['checks'])+sum(prior['checks'].values())
        owned_window_pixels+=r['complete_client_pixels'];owned_window_fields+=r['native_fields_compared']
    gates={};pending=[]
    for name in ('play-report.json','allbugs-report.json'):
        path=base/'native/gates'/name;r=json.loads(path.read_text())
        if r['result']=='RUNNING':pending.append(name);continue
        assert r['result']=='PASS',r
        assert r['binary_sha256']==native['runs']['headless']['binary_sha256']
        assert r['verifier_sha256']==digest(ROOT/'tools/verify_native_routes.py')
        previous=ROOT/'build/pride-restart-clock/native/gates'/name;prior=json.loads(previous.read_text())
        checks[name+'-previous-shipped-endpoints']=r['routes']==prior['routes']
        if name=='allbugs-report.json':
            checks['allbugs-every-field-ram']=r['allbugs_tracked_ram_equal_every_frame']
            a=base/'native/gates/allbugs-aot.ram';b=base/'native/gates/allbugs-lle.ram';old_ram=ROOT/'build/pride-restart-clock/native/gates/allbugs-aot.ram'
            checks['allbugs-shipped-every-field-ram']=a.read_bytes()==b.read_bytes()==old_ram.read_bytes();paths.extend((a,b,old_ram))
        paths.extend((path,previous));gates[name]=digest(path)
    for relative,host in (('early-state/report.json','headless'),('windows/report.json','sdl')):
        path=base/'native'/relative
        if not path.exists():pending.append(relative);continue
        r=bound(path);assert r['result']=='PASS' and all(r['checks'].values()),relative
        identity=r['binary_sha256'] if host=='headless' else r['after_binary_sha256']
        assert identity==native['runs'][host]['binary_sha256']
        paths.append(path);gates[relative]=digest(path);passed+=len(r['checks'])
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    result=dict(result='PARTIAL_NATIVE_GATES_PENDING' if pending else 'PARTIAL',scope=__doc__,checks=checks,
        checks_passed=passed+len(checks),reports_sha256=reports,native_gate_reports_sha256=gates,pending_native_gates=pending,
        actual_repeated_f9_cases=2,selected_md_audio_restart_verified=True,practice_restart_from_owned_revival_verified=True,
        rejected_raster_records_while_owned=2,
        every_live_native_video_and_wram_fields=video_fields,client_pixels_except_intentional_elapsed_run_value=client_pixels,
        first_loaded_and_plus8_complete_client_pixels=first_loaded_pixels,
        actual_owned_f1_cross_mode_native_fields=owned_window_fields,actual_owned_f1_cross_mode_complete_client_pixels=owned_window_pixels,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        opaque_backend_snapshot_version=8,exact_legacy_raster_recovery_verified=False,
        public_player_enabled=False,mixed_ui_overlay_fidelity_complete=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-raster-state-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],result['checks_passed'],'checks;',video_fields,'live native fields;',client_pixels,'scoped client pixels; pending',pending,flush=True)


if __name__=='__main__':main()
