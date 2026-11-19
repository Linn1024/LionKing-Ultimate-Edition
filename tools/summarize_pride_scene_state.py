"""Bind post-preparation controller lifecycle evidence, retaining open scope."""
import csv
import hashlib
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def main():
    base=ROOT/'build/pride-scene-state';reports={}
    def read(name):
        path=base/name;r=json.loads(path.read_text())
        for source,sha in r.get('source_sha256',{}).items():assert digest(ROOT/source)==sha,source
        reports[name]=digest(path);return r
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/('scene-state-'+host+'.exe'))==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    def artifacts(folder,run):
        for name,sha in run['artifacts_sha256'].items():assert digest(folder/name)==sha,str(folder/name)
    def envelope(path,binary,field):
        raw=bytearray(path.read_bytes());assert raw[:8]==b'PRDSAVE1'
        assert struct.unpack_from('<4I',raw,8)==(1,512,len(raw)-512,field)
        assert raw[24:56].hex()==binary
        expected=bytes(raw[56:88]);raw[56:88]=bytes(32);assert hashlib.sha256(raw).digest()==expected
        assert raw[512:520]==b'TLKSTAT1' and struct.unpack_from('<I',raw,524)[0]==field
    canonical=hashes(ROOT/'build/pride-compiled-revival/sync-full-headless/lle/run.log')
    headless=0
    for field in (4700,4703,4726,4775):
        for save,load in (('aot','lle'),('lle','aot')):
            name=f'matrix/{field}-{save}-{load}';r=read(name+'/report.json')
            assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
            assert r['endpoint_guest_exact'] and r['remaining_tracked_ram_exact'] and r['remaining_owner_events_exact']
            for part,run in r['runs'].items():
                assert run['exit_code']==0 and run['guest']==canonical;artifacts(base/name/part,run)
            envelope(base/name/'checkpoint.private-state',r['binary_sha256'],field)
            for filename in ('owner-fields.csv','restore-fields.csv','restore-events.csv'):
                expected=[v for v in rows(base/name/'baseline'/filename) if int(v['field'])>field]
                assert rows(base/name/'resumed'/filename)==expected,(name,filename)
            headless+=1
    windows=read('windows/report.json');first=read('first-frame/report.json');pixels_checked=0
    assert first['script_sha256']==digest(ROOT/'tools/verify_pride_scene_state_first_frame.py')
    for r,parent in ((windows,'windows'),(first,'first-frame')):
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        for mode,case in r['runs'].items():
            if parent=='windows':assert case['guest_hashes_exact'] and case['actual_client_exact'] and case['continuation_pcm_exact']
            else:assert case['first_displayed_frame_and_guest_exact']
            for part,run in case['runs'].items():artifacts(base/parent/(mode+'-'+part),run)
            assert pixels(base/parent/(mode+'-baseline/window.png'))==pixels(base/parent/(mode+'-resumed/window.png'))
            pixels_checked+=case['exact_client_pixels']
        for part in ('baseline','resumed'):
            assert pixels(base/parent/('aot-'+part)/'window.png')==pixels(base/parent/('lle-'+part)/'window.png')
    audio={}
    for mode in ('aot','lle'):
        envelope(base/'windows'/(mode+'.private-state'),build['runs']['sdl']['binary_sha256'],4703)
        with wave.open(str(base/'windows'/(mode+'-resumed')/'audio.wav'),'rb') as wav:
            assert wav.getnframes()==697*48000*357366//21477272
            audio[mode]=wav.readframes(wav.getnframes())
    assert audio['aot']==audio['lle'] and len(audio['aot'])==2226732
    rejected=read('rejections/report.json');assert rejected['result']=='PASS' and len(rejected['runs'])==15
    assert rejected['binary_sha256']==build['runs']['probe']['binary_sha256']
    assert rejected['script_sha256']==digest(ROOT/'tools/verify_pride_scene_state_rejections.py')
    for name,run in rejected['runs'].items():assert run['exit_code']==8;artifacts(base/'rejections'/name,run)
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        cross_mode_new_process_cases=headless,verified_controller_ages=[270,273,296,345],
        actual_windows_clients=8,exact_client_pixels=pixels_checked,continuation_pcm_bytes=len(audio['aot']),
        malformed_policy_and_save_preservation_cases=15,prepared_graphics_verified=False,
        earlier_default_final_repeated_death_verified=False,same_process_rollback_verified=False,
        pause_reset_source_switching_verified=False,production_behavior_enabled=False,
        full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-scene-state-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Private checkpoint controller cross-mode/new-process/window/PCM save continuation verified; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
