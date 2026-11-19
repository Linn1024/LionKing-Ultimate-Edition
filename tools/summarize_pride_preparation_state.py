"""Bind checkpoint preparation cache continuation without claiming full Pride."""
import hashlib
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import frame_records,glyph_records
from verify_windows import hashes,pixels


CASES=[(256,'native',4430,'aot','lle'),(256,'native',4494,'lle','aot'),
       (256,'native',4668,'aot','lle'),(256,'native',4672,'lle','aot'),
       (256,'native',4699,'aot','lle'),(256,'native',4699,'lle','aot'),
       (320,'all',4430,'lle','aot'),(320,'all',4494,'aot','lle'),
       (320,'all',4668,'lle','aot'),(320,'all',4672,'aot','lle'),
       (320,'all',4699,'aot','lle'),(320,'all',4699,'lle','aot')]


def main():
    base=ROOT/'build/pride-preparation-state';reports={}
    def read(name):
        path=base/name;value=json.loads(path.read_text())
        for name,sha in value.get('source_sha256',{}).items():assert digest(ROOT/name)==sha,name
        reports[str(path.relative_to(base)).replace('\\','/')]=digest(path);return value
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/f'preparation-state-{host}.exe')==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    def artifacts(folder,run):
        for name,sha in run['artifacts_sha256'].items():assert digest(folder/name)==sha,str(folder/name)
    def checksum(record,offset):
        record=bytearray(record);expected=record[offset:offset+32];record[offset:offset+32]=bytes(32)
        assert hashlib.sha256(record).digest()==expected
    columns=set();template_counts=set();bank_sizes=set()
    def envelope(path,identity,field,width):
        raw=path.read_bytes();assert raw[:8]==b'PRPSAVE1'
        assert struct.unpack_from('<4I',raw,8)==(1,512,len(raw)-512,field)
        assert raw[24:56].hex()==identity;checksum(raw,56)
        assert raw[512:520]==b'TLKSTAT1' and struct.unpack_from('<I',raw,524)[0]==field
        footer=raw[-32:];assert footer[:8]==b'PRPEND01'
        native,history_size,cache_size,version,reserved,extra=struct.unpack_from('<6I',footer,8)
        assert version==1 and not reserved and not extra and 512+native+history_size+cache_size+32==len(raw)
        history=raw[512+native:512+native+history_size]
        assert history[:8]==b'PRDHIST1' and struct.unpack_from('<II',history,8)==(3,len(history));checksum(history,48)
        assert struct.unpack_from('<I',history,96)[0]==field and struct.unpack_from('<I',history,104)[0]==width
        column=struct.unpack_from('<I',history,108)[0];assert column<=width-256;columns.add(column)
        cache=raw[512+native+history_size:-32]
        assert cache[:8]==b'PRPREP01' and struct.unpack_from('<II',cache,8)==(1,len(cache));checksum(cache,48)
        assert cache[16:48].hex()==identity
        saved,recipes,bank,reserved=struct.unpack_from('<4I',cache,80)
        assert saved==field and recipes==7*221 and not reserved and len(cache)==96+recipes+bank
        assert cache[96+recipes:104+recipes]==b'TLKNBK01'
        template_counts.add(recipes//221);bank_sizes.add(bank)
    canonical=hashes(ROOT/'build/pride-compiled-revival/sync-full-headless/lle/run.log')
    restored_pixels=restored_indices=0
    for width,graphics,field,save,load in CASES:
        name=f'matrix/{width}-{graphics}-{field}-{save}-{load}';r=read(name+'/report.json')
        assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
        for key in ('endpoint_guest_exact','remaining_tracked_ram_exact','remaining_owner_events_exact',
                    'remaining_composition_and_scene_trace_exact','remaining_installed_glyphs_exact','final_composed_image_exact'):
            assert r[key],(name,key)
        a=base/name/'baseline';b=base/name/'resumed'
        for part,run in r['runs'].items():
            assert run['exit_code']==0 and run['guest']==canonical;artifacts(base/name/part,run)
        assert digest(base/name/'checkpoint.private-state')==r['state_sha256']
        envelope(base/name/'checkpoint.private-state',r['binary_sha256'],field,width)
        reference=ROOT/f'build/pride-compiled-prepared/headless-{width}-{save}'/(graphics+'-owned')
        for file in ('render-owned.rgb','route.ram','prepared-fonts.bin','prepared-objects.csv'):
            assert digest(a/file)==digest(reference/file),(name,file)
        before=frame_records(a/'render-owned.rgb',width);after=frame_records(b/'render-owned.rgb',width)
        assert after=={age:record for age,record in before.items() if 4430+age>field}
        assert glyph_records(b)==[(f,raw) for f,raw in glyph_records(a) if f>field]
        restored_pixels+=len(after)*width*224;restored_indices+=len(glyph_records(b))*2048
        assert pixels(a/'picture.png')==pixels(b/'picture.png')
    windows=read('windows/report.json');assert windows['result']=='PASS'
    assert windows['binary_sha256']==build['runs']['sdl']['binary_sha256']
    with wave.open(str(ROOT/'build/pride-compiled-revival/sync-audio/lle/audio.wav'),'rb') as wav:
        canonical_pcm=wav.readframes(wav.getnframes())
    clients=pixel_count=0;tails={}
    for name,case in windows['runs'].items():
        field=case['save_at'];width=case['width'];parent=base/'windows'/name
        assert case['remaining_render_and_glyph_traces_exact'] and case['continuation_pcm_exact']
        for part,run in case['runs'].items():assert run['exit_code']==0;artifacts(parent/part,run);clients+=1
        envelope(parent/'checkpoint.private-state',windows['binary_sha256'],field,width)
        assert pixels(parent/'baseline/window.png')==pixels(parent/'resumed/window.png')
        for part,frames in (('baseline',5400),('resumed',5400-field)):
            with wave.open(str(parent/part/'audio.wav'),'rb') as wav:
                assert wav.getnframes()==frames*48000*357366//21477272
                pcm=wav.readframes(wav.getnframes())
            assert pcm==(canonical_pcm if part=='baseline' else canonical_pcm[-len(pcm):])
            if part=='resumed':
                if field in tails:assert tails[field]==pcm
                tails[field]=pcm
        pixel_count+=case['first_client_pixels']+case['final_client_pixels']
    rejected=read('rejections/report.json');assert rejected['result']=='PASS'
    assert rejected['binary_sha256']==build['runs']['probe']['binary_sha256']
    assert rejected['script_sha256']==digest(ROOT/'tools/verify_pride_preparation_state_rejections.py')
    for name,run in rejected['runs'].items():
        assert run['exit_code']==(0 if name=='valid-control' else 8);artifacts(base/'rejections'/name,run)
    rewind=read('rewind/verified-report.json');capture=read('rewind/report.json')
    assert rewind['result']=='PASS' and rewind['binary_sha256']==build['runs']['sdl']['binary_sha256']
    assert capture['script_sha256']==digest(ROOT/'tools/probe_pride_preparation_rewind.py')
    assert capture['binary_sha256']==rewind['binary_sha256']
    for name,run in capture['runs'].items():
        assert run['exit_code']==0;artifacts(base/'rewind'/name,run)
    for run in rewind['runs'].values():
        for key in ('endpoint_guest_exact','final_client_exact','controller_fields_exact',
                    'whole_owned_records_exact','remaining_installed_glyphs_exact','continuation_pcm_exact'):
            assert run[key],key
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
                      'tools/probe_pride_preparation_state.py':digest(ROOT/'tools/probe_pride_preparation_state.py')},
        cross_mode_preparation_resumes=len(CASES),saved_ages=sorted({c[2]-4430 for c in CASES}),
        saved_camera_columns=sorted(columns),ready_decoder_recipe_counts=sorted(template_counts),bank_record_sizes=sorted(bank_sizes),
        remaining_composed_pixels=restored_pixels,remaining_installed_glyph_indices=restored_indices,
        actual_windows_clients=clients,exact_client_pixels=pixel_count,
        additional_live_rewind_clients=len(rewind['runs']),same_process_checkpoint_rewind_verified=True,
        live_rewind_owned_pixels=sum(r['checked_owned_pixels'] for r in rewind['runs'].values()),
        live_rewind_native_capture_telemetry_exact=all(r['native_capture_telemetry_exact'] for r in rewind['runs'].values()),
        continuation_pcm_bytes_by_saved_field={str(f):len(data) for f,data in tails.items()},
        invalid_preparation_cases=len(rejected['runs'])-1,valid_rejection_control=True,
        earlier_checkpoint_preparation_verified=True,cross_profile_load_verified=False,
        default_final_repeated_contexts_verified=False,pause_reset_switching_verified=False,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-preparation-state-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Earlier checkpoint bank/decoder/history continuation verified; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
