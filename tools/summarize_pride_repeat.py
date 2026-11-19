"""Bind repeated nonfinal revival, per-scene recipes and second-scene save evidence."""
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_repeat import BASE
from run_pride_repeat_matrix import CASES,WINDOWS,name
from verify_pride_live_error_ui import read_rows
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data
from verify_pride_prepared_current_fonts import indices


def bound(path):
    r=json.loads(path.read_text())
    for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,(path,file)
    return r


def main():
    build=bound(BASE/'build-report.json')
    for file,sha in build['production_sha256'].items():assert digest(ROOT/file)==sha,file
    for host,r in build['runs'].items():
        assert digest(BASE/f'repeat-{host}.exe')==r['binary_sha256']
        for file,sha in r['link_inputs_sha256'].items():assert digest(ROOT/file)==sha,file
    oracle=ROOT/'build/pride-default-actor/font-oracle/original-fonts.bin';raw=oracle.read_bytes();assert raw[:8]==b'SNHUD002'
    fonts={tuple(struct.unpack_from('<4I',raw,at)):raw[at+532:at+1044] for at in range(8,len(raw),1044)};cache={}
    results={};additional=[];glyphs=0
    for host,cases in (('headless',CASES),('windows',WINDOWS)):
        for case in cases:
            folder=BASE/('scoped-'+host)/name(case);r=bound(folder/'report.json')
            assert r['result']=='PASS' and all(r['checks'].values()) and r['frames']==3000
            assert r['binary_sha256']==build['runs']['sdl' if host=='windows' else 'probe']['binary_sha256']
            for file,sha in r['artifacts_sha256'].items():assert digest(folder/file)==sha,(folder,file)
            assert len(r['guest'])==2 and not r['loaded_states'] and not r['guest_fixture_edits']
            expected_entry=2459 if case[0]=='snes' else 2458
            assert r['scenes'][1]['begin_field']==expected_entry
            old=ROOT/'build/pride-actor-handoff/active'/f'{case[0]}-default-{case[1]}-{case[2]}-{case[3]}-owned'
            prior=bound(old/'report.json');additional.append(old/'report.json')
            if host=='headless':assert digest(folder/'render-owned.rgb')==prior['artifacts_sha256']['render-owned.rgb']
            else:
                old_ui=ROOT/'build/pride-handoff-state/windows'/('snes-default-256-native-0-aot-lle' if case[0]=='snes' else 'md-default-320-all-0-lle-aot')
                old_r=bound(old_ui/'report.json');additional.append(old_ui/'report.json')
                old_audio=wav_data(old_ui/'baseline/audio.wav');assert wav_data(folder/'audio.wav')[:len(old_audio)]==old_audio
            for i,scene in enumerate(r['scenes']):
                part=folder if i==0 else folder/scene['folder']
                assert scene['released'] and scene['mismatch']==0 and 300<=scene['release_age']<=308
                assert (part/'scenery-evidence.json').exists()
                data=(part/'prepared-fonts.bin').read_bytes();assert data[:8]==b'PRDHUD01' and (len(data)-8)%1052==0
                for at in range(8,len(data),1052):
                    age,kind,maximum,current,initial,x,y=struct.unpack_from('<7I',data,at)
                    key=(kind,maximum,current,initial)
                    if kind:key=next(k for k in fonts if k[:3]==key[:3])
                    if key not in cache:cache[key]=indices(fonts[key])
                    assert data[at+28:at+1052]==cache[key],(folder,i,age,key)
                    glyphs+=1024
            events=read_rows(folder/'events.csv');assert len([x for x in events if x['event']=='apply'])==2
            prepared=[x for x in read_rows(folder/'decompress.csv') if x['event']=='prepared'];assert len(prepared)==14
            assert all(x['death']=='1' and any(s['begin_field']<=int(x['field'])<=s['begin_field']+300 for s in r['scenes']) for x in prepared)
            if host=='headless' and case[3]=='lle' and (folder.parent/(name(case[:-1]+('aot',)))).exists():
                other=folder.parent/name(case[:-1]+('aot',));rr=bound(other/'report.json');assert r['guest']==rr['guest']
                assert digest(folder/'route.ram')==digest(other/'route.ram')
                for i in (0,1):
                    a=folder if i==0 else folder/r['scenes'][i]['folder'];b=other if i==0 else other/rr['scenes'][i]['folder']
                    assert digest(a/'render-owned.rgb')==digest(b/'render-owned.rgb')
            results[host+'/'+name(case)]=dict(report_sha256=digest(folder/'report.json'),scenes=r['scenes'])
    saves={}
    for i in range(4):
        folder=BASE/'saves'/str(i);r=bound(folder/'report.json');assert r['result']=='PASS' and all(r['checks'].values())
        before=bound(folder/'baseline/report.json');assert digest(folder/'baseline/report.json')==r['baseline_report_sha256']
        for file,sha in before['artifacts_sha256'].items():assert digest(folder/'baseline'/file)==sha,(i,file)
        for file,sha in r['resumed_artifacts_sha256'].items():assert digest(folder/'resumed'/file)==sha,(i,file)
        saves[str(i)]=dict(report_sha256=digest(folder/'report.json'),save_age=r['save_age'],save_mode=r['save_mode'],load_mode=r['load_mode'])
    for report in ('ground-cpu-report.json','pixels-report.json'):
        rr=bound(BASE/report);assert rr['result']=='PASS'
        for case in rr['cases']:
            if isinstance(case,dict):
                root=BASE/('scoped-'+case['host'])/case['case'];assert digest(root/'report.json')==case['report_sha256']
    extended=bound(BASE/'extended/report.json');assert extended['result']=='PASS' and extended['frames']==8000
    for file,sha in extended['artifacts_sha256'].items():assert digest(BASE/'extended'/file)==sha,file
    prepar=[x for x in read_rows(BASE/'extended/decompress.csv') if x['event']=='prepared'];assert len(prepar)==14
    assert all(x['death']=='1' and any(s['begin_field']<=int(x['field'])<=s['begin_field']+300 for s in extended['scenes']) for x in prepar)
    assert any(x['death']=='0' and int(x['field'])>3600 for x in read_rows(BASE/'extended/decompress.csv'))
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),BASE/'build-report.json',ROOT/'tools/run_pride_repeat_matrix.py',oracle,
        ROOT/'tools/verify_pride_prepared_current_fonts.py',ROOT/'tools/verify_pride_audio_state.py')}
    for p in additional:sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    out=dict(result='PARTIAL',cases=results,saves=saves,source_sha256=sources,
        independent_reports_sha256={f:digest(BASE/f) for f in ('ground-cpu-report.json','pixels-report.json')},
        extended_sha256=digest(BASE/'extended/report.json'),independent_pixels=json.loads((BASE/'pixels-report.json').read_text())['pixels_compared'],
        original_cpu_glyph_indices=glyphs,repeated_default_revival_verified=True,second_revival_new_process_save_verified=True,
        reset_restart_verified=False,md_final_death_verified=False,repeated_checkpoint_verified=False,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-repeat-latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Repeated default revival PASS;',out['independent_pixels'],'independent pixels;',glyphs,'original glyph indices; four second-scene saves',flush=True)


if __name__=='__main__':main()
