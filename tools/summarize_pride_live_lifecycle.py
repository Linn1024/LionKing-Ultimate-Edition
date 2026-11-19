"""Bind real menu pauses and source-palette changes within owned default revival."""
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import read_rows,toast_image
from probe_pride_preparation_state import frame_records,glyph_records
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-live-lifecycle'
UI=ROOT/'build/pride-live-error-ui'


def bound(path):
    r=json.loads(path.read_text())
    for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,(path,name)
    return r


def main():
    build=bound(UI/'build-report.json');binary=UI/'error-ui-sdl.exe'
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for run in build['runs'].values():
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    results={};additional=[]
    folders={name:BASE/'final'/name for name in ('pause-native','pause-md','palette-death')}
    folders['palette-fade']=ROOT/'build/pride-live-palette-retry/final/palette-fade'
    for name,folder in folders.items():
        r=bound(folder/'report.json');assert r['result']=='PASS' and all(r['checks'].values()),name
        assert r['case']==name and r['binary_sha256']==digest(binary),name
        for file,sha in r['artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
        live=folder/'live';width=r['width'];entry=1776 if width==256 else 1777
        actual=frame_records(live/'render-owned.rgb',width)
        if r['action']=='pause':
            reference=UI/'audio-windows'/('native-aot' if width==256 else 'md-lle')
            control=reference/'control';prior=bound(reference/'report.json');additional.append(reference/'report.json')
            for file,sha in prior['artifacts_sha256'].items():assert digest(reference/file)==sha,(name,file)
            assert (folder/'resources.ini').read_bytes()==(reference/'resources.ini').read_bytes(),name
            assert len(r['events'])==5 and [e['requested_age'] for e in r['events']]==[64,238,269,274,301]
            for event in r['events']:
                assert event['paused_field']==event['final_field'] and entry+event['requested_age']<=event['paused_field']<=entry+event['requested_age']+2
                assert event['repeated_owned_presentations']>0 or event['already_released']
                assert (live/f"paused-{event['requested_age']}.png").exists()
            assert sum(e['resource_tree'] for e in r['events'])==1
            assert actual==frame_records(control/'render-owned.rgb',width)
            glyphs=dict(glyph_records(control))
            for field,data in glyph_records(live):assert glyphs[field]==data,(name,field)
            assert wav_data(live/'audio.wav')==wav_data(control/'audio.wav')
            assert pixels(live/'window.png')==pixels(control/'window.png')
            pauses=5
        else:
            control=folder/'control';first=r['events'][0]['first_new_palette_age'];requested=r['events'][0]['requested_age']
            assert requested<=first<=requested+3 and first<300
            old=ROOT/'build/pride-actor-handoff/active'/f"md-default-320-all-{r['mode']}-owned"
            prior=bound(old/'report.json');additional.append(old/'report.json')
            assert digest(old/'render-owned.rgb')==prior['artifacts_sha256']['render-owned.rgb']
            additional.append(old/'render-owned.rgb')
            before,after=frame_records(old/'render-owned.rgb',width),frame_records(control/'render-owned.rgb',width)
            for age,data in actual.items():
                assert data==(before if age<first else after)[age],(name,age)
                assert struct.unpack_from('<I',data,20)[0]==(1 if age<first else 0)
            assert b'graphics.sprites.simba.cub.palette = snes' in (folder/'resources.ini').read_bytes()
            a,b=wav_data(live/'audio.wav'),wav_data(control/'audio.wav');assert a and b[-len(a):]==a
            image=pixels(live/'window.png')
            assert image==pixels(control/'window.png') or image==toast_image(control/'window.png',live/'guest.png','Applied and saved')
            pauses=0
        assert hashes(live/'run.log')==hashes(control/'run.log') and len(hashes(live/'run.log'))==2
        assert pixels(live/'guest.png')==pixels(control/'guest.png')
        results[name]=dict(report_sha256=digest(folder/'report.json'),pauses=pauses,
            logical_scene_pixels=len(actual)*width*224,client_pixels=width*224*4,mode=r['mode'])
    # Preserve the failed publication as a distinct observed atomicity check.
    failed=BASE/'final/palette-fade';reference=UI/'audio-windows/md-lle';control=reference/'control'
    log=(failed/'live/run.log').read_text()
    assert 'Cannot save profile; active choices unchanged' in log
    assert (failed/'resources.ini').read_bytes()==(reference/'resources.ini').read_bytes()
    for file in ('render-owned.rgb','guest.png'):
        assert digest(failed/'live'/file)==digest(control/file),file
    assert hashes(failed/'live/run.log')==hashes(control/'run.log')
    assert wav_data(failed/'live/audio.wav')==wav_data(control/'audio.wav')
    failed_artifacts={str(p.relative_to(failed)).replace('\\','/'):digest(p) for p in failed.rglob('*') if p.is_file()}
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),ROOT/'tools/verify_pride_live_lifecycle.py',ROOT/'tools/verify_pride_live_palette_retry.py',
        ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_pride_live_error_ui.py',
        ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py',UI/'build-report.json')}
    for p in additional:sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    out=dict(result='PARTIAL',scope='Real menu/resource-tree pauses and cub-palette changes during owned default revival.',
        cases=results,source_sha256=sources,menu_pauses=10,palette_switches=2,
        logical_scene_pixels=sum(r['logical_scene_pixels'] for r in results.values()),
        client_pixels=sum(r['client_pixels'] for r in results.values()),
        failed_profile_publication_observed=dict(active_unchanged=True,artifacts_sha256=failed_artifacts),
        reset_lifecycle_verified=False,other_source_leaves_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-live-lifecycle-latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Ten menu pauses/two owned palette switches PASS; scene pixels',out['logical_scene_pixels'],'client pixels',out['client_pixels'],flush=True)


if __name__=='__main__':main()
