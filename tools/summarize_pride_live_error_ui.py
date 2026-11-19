"""Bind the actual F1/F5 error UI, recovery and post-release palette-change audit."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import BASE,CASES,read_rows,toast_image
from probe_pride_preparation_state import frame_records,glyph_records
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    build=json.loads((BASE/'build-report.json').read_text())
    for group in ('source_sha256','production_sha256'):
        for name,sha in build[group].items():assert digest(ROOT/name)==sha,name
    for host,r in build['runs'].items():
        assert digest(BASE/f'error-ui-{host}.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    results={};additional_sources=[]
    for name,(start,width,graphics,mode,kind) in CASES.items():
        folder=BASE/'audio-windows'/name;path=folder/'report.json';r=json.loads(path.read_text())
        assert r['result']=='PASS' and all(r['checks'].values()) and r['actual_f1_f5_used'],name
        assert r['actual_f10_after_release_used']==(kind=='graphics'),name
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,(name,file)
        for file,sha in r['artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
        live,control=folder/'live',folder/'control';entry=1776 if start=='snes' else 1777
        events=read_rows(live/'live-load.csv');assert events==r['events']
        assert [e['success'] for e in events]==(['1','0','1','0'] if kind=='recovery' else ['1','0'])
        assert hashes(live/'run.log')==hashes(control/'run.log') and len(hashes(live/'run.log'))==2
        assert pixels(live/'guest.png')==pixels(control/'guest.png')
        assert pixels(live/'window.png')==toast_image(control/'window.png',live/'guest.png',r['message'])
        expected,actual=wav_data(control/'audio.wav'),wav_data(live/'audio.wav')
        samples=lambda f:f*48000*357366//21477272*4
        if kind=='recovery':
            attempt=int(events[2]['attempt_field']);saved=int(events[2]['loaded_field']);assert saved==r['save_field']
            assert actual==expected[:samples(attempt)-samples(entry)]+expected[samples(saved)-samples(entry):]
        elif kind=='graphics':
            assert actual and expected[-len(actual):]==actual
            assert b'graphics.sprites.simba.cub.palette = snes' in (folder/'resources.ini').read_bytes()
        else:assert actual==expected and actual
        # F1 can duplicate a completed presentation and recovery repeats an
        # epoch. Check every duplicate, then every logical scene record.
        seen=frame_records(live/'render-owned.rgb',width)
        if kind!='graphics':
            assert seen==frame_records(control/'render-owned.rgb',width),name
            source_glyph=dict(glyph_records(control))
            for field,data in glyph_records(live):assert source_glyph[field]==data,(name,field)
        else:
            old=ROOT/'build/pride-actor-handoff/active'/f'md-default-320-all-{mode}-owned'
            prior=json.loads((old/'report.json').read_text())
            assert digest(old/'render-owned.rgb')==prior['artifacts_sha256']['render-owned.rgb']
            for file,sha in prior['source_sha256'].items():assert digest(ROOT/file)==sha,file
            additional_sources.extend((old/'report.json',old/'render-owned.rgb'))
            before=frame_records(old/'render-owned.rgb',width)
            assert seen=={age:data for age,data in before.items() if age>0},name
        assert not list(folder.rglob('*.part')),(name,'temporary files')
        results[name]=dict(report_sha256=digest(path),actual_keys=True,final_client_pixels=width*224*4,
            owned_scene_pixels=len(seen)*width*224,pcm_bytes=len(actual),recovery=kind=='recovery',palette_switch=kind=='graphics')
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/probe_pride_preparation_state.py',
        ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py',BASE/'build-report.json')}
    for p in additional_sources:sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    out=dict(result='PARTIAL',scope='Private live F1/F5 diagnostics and recovery; actual F10 cub palette change after release.',
        cases=results,source_sha256=sources,actual_live_error_ui_verified=True,
        final_client_pixels=sum(r['final_client_pixels'] for r in results.values()),
        owned_scene_pixels=sum(r['owned_scene_pixels'] for r in results.values()),
        pause_reset_source_lifecycle_complete=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-live-error-ui-latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Five actual F1/F5 cases PASS; pixels',out['final_client_pixels'],'scene pixels',out['owned_scene_pixels'],flush=True)


if __name__=='__main__':main()
