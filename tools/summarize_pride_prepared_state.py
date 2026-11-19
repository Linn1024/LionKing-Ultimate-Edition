"""Bind prepared-history checkpoint resumes without claiming full lifecycle."""
import hashlib
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import frame_records,glyph_records,rows
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-prepared-state';reports={}
    def read(name):
        path=base/name;value=json.loads(path.read_text())
        for name,sha in value.get('source_sha256',{}).items():assert digest(ROOT/name)==sha,name
        reports[str(path.relative_to(base)).replace('\\','/')]=digest(path);return value
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/('prepared-state-'+host+'.exe'))==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    def artifacts(folder,run):
        for name,sha in run['artifacts_sha256'].items():assert digest(folder/name)==sha,str(folder/name)
    def envelope(path,identity,field,width):
        raw=bytearray(path.read_bytes());assert raw[:8]==b'PRDSAVE1'
        assert struct.unpack_from('<4I',raw,8)==(1,512,len(raw)-512,field)
        assert raw[24:56].hex()==identity
        sha=bytes(raw[56:88]);raw[56:88]=bytes(32);assert hashlib.sha256(raw).digest()==sha
        assert raw[512:520]==b'TLKSTAT1' and struct.unpack_from('<I',raw,524)[0]==field
        footer=raw[-24:];assert footer[:8]==b'PRDHEND1'
        native,size,version,reserved=struct.unpack_from('<4I',footer,8)
        assert version==1 and not reserved and 512+native+size+24==len(raw)
        history=bytearray(raw[512+native:-24]);assert history[:8]==b'PRDHIST1'
        assert struct.unpack_from('<II',history,8)==(2,len(history))
        expected=bytes(history[48:80]);history[48:80]=bytes(32);assert hashlib.sha256(history).digest()==expected
        assert struct.unpack_from('<I',history,96)[0]==field
        assert struct.unpack_from('<I',history,104)[0]==width
        column=struct.unpack_from('<I',history,108)[0];assert column<=width-256
        return column
    canonical=hashes(ROOT/'build/pride-compiled-revival/sync-full-headless/lle/run.log')
    cases=0;restored_pixels=restored_indices=0;columns=set()
    for width,graphics in ((256,'native'),(320,'all')):
        for field in (4700,4703,4727,4775):
            for save,load in (('aot','lle'),('lle','aot')):
                name=f'matrix/{width}-{graphics}-{field}-{save}-{load}';r=read(name+'/report.json')
                assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
                for key in ('endpoint_guest_exact','remaining_tracked_ram_exact','remaining_owner_events_exact',
                            'remaining_composition_and_scene_trace_exact','remaining_installed_glyphs_exact','final_composed_image_exact'):
                    assert r[key],(name,key)
                a=base/name/'baseline';b=base/name/'resumed'
                for part,run in r['runs'].items():
                    assert run['exit_code']==0 and run['guest']==canonical;artifacts(base/name/part,run)
                columns.add(envelope(base/name/'checkpoint.private-state',r['binary_sha256'],field,width))
                reference=ROOT/f'build/pride-compiled-prepared/headless-{width}-{save}'/(graphics+'-owned')
                for file in ('render-owned.rgb','route.ram','prepared-fonts.bin','prepared-objects.csv'):
                    assert digest(a/file)==digest(reference/file),(name,file)
                before=frame_records(a/'render-owned.rgb',width);after=frame_records(b/'render-owned.rgb',width)
                assert after=={age:record for age,record in before.items() if 4430+age>field}
                assert glyph_records(b)==[(f,raw) for f,raw in glyph_records(a) if f>field]
                restored_pixels+=len(after)*width*224
                restored_indices+=len(glyph_records(b))*2048
                assert pixels(a/'picture.png')==pixels(b/'picture.png')
                cases+=1
    windows=read('windows/report.json');assert windows['result']=='PASS'
    assert windows['binary_sha256']==build['runs']['sdl']['binary_sha256']
    clients=pixel_count=0;audio=[]
    for name,case in windows['runs'].items():
        width=int(name.split('-')[0]);parent=base/'windows'/name
        assert case['remaining_render_and_glyph_traces_exact'] and case['continuation_pcm_exact']
        for part,run in case['runs'].items():assert run['exit_code']==0;artifacts(parent/part,run);clients+=1
        envelope(parent/'checkpoint.private-state',windows['binary_sha256'],4703,width)
        assert pixels(parent/'baseline/window.png')==pixels(parent/'resumed/window.png')
        for part,frames in (('baseline',5400),('resumed',697)):
            with wave.open(str(parent/part/'audio.wav'),'rb') as wav:
                assert wav.getnframes()==frames*48000*357366//21477272
                pcm=wav.readframes(wav.getnframes())
            audio.append((part,pcm))
        pixel_count+=case['first_client_pixels']+case['final_client_pixels']
    for part in ('baseline','resumed'):
        assert len(set(data for key,data in audio if key==part))==1
    with wave.open(str(ROOT/'build/pride-compiled-revival/sync-audio/lle/audio.wav'),'rb') as wav:
        canonical_pcm=wav.readframes(wav.getnframes())
    assert next(data for key,data in audio if key=='baseline')==canonical_pcm
    assert canonical_pcm[-2226732:]==next(data for key,data in audio if key=='resumed')
    rejected=read('rejections/report.json');assert rejected['result']=='PASS'
    assert rejected['binary_sha256']==build['runs']['probe']['binary_sha256']
    assert rejected['script_sha256']==digest(ROOT/'tools/verify_pride_prepared_state_rejections.py')
    assert rejected['runs']['valid-control']['exit_code']==0
    for name,run in rejected['runs'].items():
        assert run['exit_code']==(0 if name=='valid-control' else 8);artifacts(base/'rejections'/name,run)
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
            'tools/probe_pride_prepared_state.py':digest(ROOT/'tools/probe_pride_prepared_state.py')},
        cross_mode_prepared_resumes=cases,saved_camera_columns=sorted(columns),
        remaining_composed_pixels=restored_pixels,remaining_installed_glyph_indices=restored_indices,
        actual_windows_clients=clients,exact_client_pixels=pixel_count,continuation_pcm_bytes=2226732,
        invalid_history_and_policy_cases=len(rejected['runs'])-1,valid_rejection_control=True,
        prepared_new_process_history_verified=True,cross_profile_load_verified=False,
        earlier_default_final_repeated_contexts_verified=False,pause_reset_switching_verified=False,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-prepared-state-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Prepared checkpoint history cross-mode/window/glyph/PCM continuation verified; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
