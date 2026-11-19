"""Verify captured live-process rewind; retain native diagnostic differences."""
import json
from pathlib import Path
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import frame_records,glyph_records,rows
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-preparation-state';out=base/'rewind';capture=out/'report.json'
    report=json.loads(capture.read_text());assert report['result']=='AUDITED'
    binary=base/'preparation-state-sdl.exe';assert digest(binary)==report['binary_sha256']
    assert digest(ROOT/'tools/probe_pride_preparation_rewind.py')==report['script_sha256']
    results={};source={'build/pride-preparation-state/rewind/report.json':digest(capture),
        'tools/probe_pride_preparation_rewind.py':digest(ROOT/'tools/probe_pride_preparation_rewind.py'),
        'tools/probe_pride_preparation_state.py':digest(ROOT/'tools/probe_pride_preparation_state.py'),
        'tools/verify_pride_preparation_rewind.py':digest(Path(__file__))}
    for width,graphics,mode in ((256,'native','lle'),(320,'all','aot')):
        case=f'{width}-{graphics}-{mode}';run=report['runs'][case];folder=out/case
        assert run['exit_code']==0
        for name,sha in run['artifacts_sha256'].items():assert digest(folder/name)==sha,name
        load='aot' if mode=='lle' else 'lle'
        reference=base/'windows'/f'{width}-{graphics}-4668-{mode}-{load}'/'baseline'
        assert hashes(folder/'run.log')==hashes(reference/'run.log')
        assert pixels(folder/'window.png')==pixels(reference/'window.png')
        def remaining(path,field):
            records=rows(path);starts=[n for n,r in enumerate(records) if int(r['field'])==field]
            assert starts
            return records[starts[-1]:]
        for name in ('owner-fields.csv','restore-fields.csv'):
            assert remaining(folder/name,4669)==remaining(reference/name,4669),name
        # Duplicate logical-age records in the two execution epochs must be
        # identical. frame_records checks every duplicate before retaining it.
        actual=frame_records(folder/'render-owned.rgb',width)
        expected=frame_records(reference/'render-owned.rgb',width)
        assert actual==expected
        a=glyph_records(folder);b=glyph_records(reference)
        starts=[n for n,(field,_) in enumerate(a) if field==4700];assert starts
        assert a[starts[-1]:]==b
        raw_a=remaining(folder/'render-fields.csv',4669);raw_b=remaining(reference/'render-fields.csv',4669)
        assert len(raw_a)==len(raw_b)
        differences=[]
        for a,b in zip(raw_a,raw_b):
            delta={key:[b[key],a[key]] for key in a if a[key]!=b[key]}
            if delta:differences.append(dict(field=int(a['field']),values=delta))
        with wave.open(str(folder/'audio.wav'),'rb') as wav:
            assert wav.getnframes()==5436*48000*357366//21477272
            actual_pcm=wav.readframes(wav.getnframes())
        with wave.open(str(reference/'audio.wav'),'rb') as wav:
            expected_pcm=wav.readframes(wav.getnframes())
        prefix=4704*48000*357366//21477272*4
        tail=expected_pcm[4668*48000*357366//21477272*4:]
        assert actual_pcm[:prefix]==expected_pcm[:prefix]
        assert actual_pcm[prefix:]==tail
        results[case]=dict(endpoint_guest_exact=True,final_client_exact=True,
            controller_fields_exact=True,whole_owned_records_exact=True,remaining_installed_glyphs_exact=True,
            continuation_pcm_exact=True,continuation_pcm_bytes=len(tail),
            checked_owned_pixels=len(expected)*width*224,
            native_capture_telemetry_exact=not differences,native_capture_differences=differences)
    (out/'verified-report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,
        binary_sha256=report['binary_sha256'],source_sha256=source,
        input_switching_verified=False,immediate_load_client_verified=False,same_process_rollback_verified=False,
        full_first_level_fidelity_complete=False),indent=2)+'\n')
    print('Both live rewinds retain full owned records/glyphs/controller/window/PCM; native diagnostics differ',flush=True)


if __name__=='__main__':main()
