"""Strict exact controls for real F12 restart from owned/ordinary play and F9."""
import argparse
import json
from pathlib import Path
import re
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels
from probe_pride_preparation_state import frame_records


def hash_rows(path):
    return [dict(field=n,frame=f,ram=w) for n,f,w in re.findall(
        r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',path.read_text())]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--leaf',choices=('music','start'),default='music');args=p.parse_args()
    root=ROOT/args.root;report_path=root/'report.json';r=bound(report_path)
    assert r['result']=='PASS' and all(r['checks'].values())
    build_path=ROOT/'build/pride-raster-state/build-report.json';build=bound(build_path)
    assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['runs']['sdl']['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    controls={};paths=[Path(__file__),report_path,build_path];checks={}
    for source in ('snes','md'):
        path=root/'controls'/source/'report.json';control=bound(path);paths.append(path)
        assert control['result']=='PASS' and all(control['checks'].values()),source
        assert control['binary_sha256']==r['binary_sha256'] and control['dll_sha256']==r['dll_sha256']
        controls[source]=path.parent
        checks[source+'-whole-new-automatic-record']=control['checks']['actual_cold_restart_snapshot']
    initial=ROOT/'build/pride-raster-state/live/md-media';initial_report=bound(initial/'report.json');paths.append(initial/'report.json')
    assert initial_report['result']=='PASS' and initial_report['binary_sha256']==r['binary_sha256']
    initial=initial/'baseline';live=root/'live';loads=read_rows(live/'live-load.csv');assert len(loads)==3
    attempts=[int(row['attempt_field']) for row in loads]
    loaded=[int(row['loaded_field']) for row in loads];assert loaded==[0,0,1427]
    references=[initial,controls['snes'],controls['md'],controls['md']]
    starts=[0,0,0,1427];ends=attempts+[3000]
    def project(getter):
        result=[]
        for folder,start,end in zip(references,starts,ends):
            result.extend(row for row in getter(folder) if start<int(row['field'])<=end)
        return result
    native=hash_rows(live/'run.log');expected=project(lambda folder:hash_rows(folder/'run.log'))
    checks['every_native_video_and_full_wram_field']=native==expected
    rows=read_rows(live/'practice-fields.csv')
    rewinds=[i for i in range(1,len(rows)) if int(rows[i]['field'])<int(rows[i-1]['field'])]
    checks['three_completed_field_rewinds']=len(rewinds)==3 and [int(rows[i]['field']) for i in rewinds]==[1,1,1428]
    assert len(rewinds)==3,rewinds
    audio=wav_data(live/'audio.wav');cuts=[0]+[int(rows[i]['wav_frames_before_audio'])*4 for i in rewinds]+[len(audio)]
    def boundary(folder,field):
        matches=[row for row in read_rows(folder/'practice-fields.csv') if int(row['field'])==field+1]
        assert len(matches)==1,(folder,field,len(matches))
        return int(matches[0]['wav_frames_before_audio'])*4
    for i,(folder,start,end) in enumerate(zip(references,starts,ends)):
        reference=wav_data(folder/'audio.wav');a=boundary(folder,start) if start else 0
        b=boundary(folder,end) if end<3000 else len(reference)
        checks[f'complete_pcm_segment_{i}']=audio[cuts[i]:cuts[i+1]]==reference[a:b]
    def stems(folder):return [dict(row,field=row['frame']) for row in read_rows(folder/'audio-stems.csv')]
    checks['every_audio_stem_field']=stems(live)==project(stems)
    # The initial owned scene is aborted by the source change. All its actual
    # scene pixels must remain the original prefix, including paused repaints.
    actual=frame_records(live/'render-owned.rgb',320);prefix=frame_records(initial/'render-owned.rgb',320)
    checks['aborted_owned_scene_prefix']=all(record==prefix[age] for age,record in actual.items()) and max(actual)>=225
    begins=[int(row['field']) for row in read_rows(controls['md']/'owner-events.csv') if row['event']=='begin']
    checks['eventual_owned_scene_present']=bool(begins) and all(field>1427 for field in begins)
    for index,field in enumerate(begins):
        relative='' if index==0 else f'scene-{field}'
        a=live/'restart-3'/relative;b=controls['md']/'restart-1'/relative
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin','scenery-evidence.json'):
            checks[f'eventual_scene_{index}/'+name]=a.joinpath(name).exists()==b.joinpath(name).exists() and (not b.joinpath(name).exists() or digest(a/name)==digest(b/name))
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
        checks[name]=read_rows(live/name)==project(lambda folder:read_rows(folder/name))
    width,height,a=pixels(live/'window.png');w,h,b=pixels(controls['md']/'window.png');assert (w,h)==(width,height)==(960,672)
    extra=(320-256)//2
    ignored={(y*3+dy)*width+(extra+x)*3+dx for y in range(13,21) for x in range(68,156) for dy in range(3) for dx in range(3)}
    checks['final_client_except_intended_run_value']=all(x==y for i,(x,y) in enumerate(zip(a,b)) if i not in ignored)
    # Music remains independent of the still-selected MD effects in the native
    # music control. Actual command/stem output supplements the saved choices.
    source_id='audio.music.pride_lands' if args.leaf=='music' else 'gameplay.levels.pride_lands.start'
    for source in ('snes','md'):
        checks[source+'-requested-leaf-persisted']=source_id+' = '+source in (root/(source+'.ini')).read_text()
    if args.leaf=='music':
        checks['native_music_with_md_effects']=any(int(row['native_peak'])>0 for row in read_rows(controls['snes']/'audio-stems.csv')) and any(int(row['md_peak'])>0 for row in read_rows(controls['snes']/'audio-stems.csv'))
        is_pride=lambda row:row['selector']=='1' and row['value']=='137'
        checks['original_md_pride_track137']=any(is_pride(row) for row in read_rows(controls['md']/'md-commands.csv'))
        checks['native_control_no_md_pride_track137']=not any(is_pride(row) for row in read_rows(controls['snes']/'md-commands.csv'))
    else:
        for source,expected in (('snes',[64,1248]),('md',[65,1255])):
            trace=read_rows(controls[source]/'start.csv')
            checks[source+'-original-constructor-values']=[int(row['selected']) for row in trace[:2]]==expected
            state=(root/f'automatic-{source}.state').read_bytes()
            checks[source+'-ordinary-start-context']=struct.unpack_from('<I',state,128)[0]==int(source=='md')
        trace=read_rows(live/'start.csv')
        checks['actual_live_constructor_sequence']=[int(row['selected']) for row in trace[:6]]==[65,1255,64,1248,65,1255]
    checks['selected_md_audio_output']=any(int(row['md_peak'])>0 for row in read_rows(controls['md']/'audio-stems.csv'))
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,
        source_id=source_id,binary_sha256=r['binary_sha256'],dll_sha256=r['dll_sha256'],native_fields_compared=len(native),
        pcm_segment_bytes=[cuts[i+1]-cuts[i] for i in range(4)],compared_final_client_pixels=len(a)-len(ignored),
        aborted_scene_records=len(actual),eventual_scene_begins=begins,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        public_player_enabled=False,mixed_ui_overlay_fidelity_complete=False,full_first_level_fidelity_complete=False)
    (root/'exact-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks;',len(native),'fields; failed',[name for name,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
