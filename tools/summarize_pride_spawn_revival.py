"""Bind selected-start default revival without claiming MD-start checkpoint fidelity."""
import array
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows,frame_records
from verify_windows import pixels
from verify_pride_default_actor_pixels import verify_default_pixels
from verify_pride_prepared_current_fonts import indices


def main():
    base=ROOT/'build/pride-spawn-revival';old=ROOT/'build/pride-grounded';bound={};sources={}
    def read(path,artifacts=False):
        r=json.loads(path.read_text());bound[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path)
        for n,sha in r.get('source_sha256',{}).items():assert digest(ROOT/n)==sha,n
        if artifacts:
            for n,sha in r['artifacts_sha256'].items():assert digest(path.parent/n)==sha,(path,n)
        return r
    build=read(base/'build-report.json');generation=read(base/'generation-report.json')
    assert {0xc087b5,0xc087bf,0xc0881d,0xc08827}<=set(generation['hook_pcs'])
    assert generation['original_analysis_manifest_exact']
    for n,sha in generation['generated_sha256'].items():assert digest(base/'generated'/n)==sha,n
    for host,r in build['runs'].items():
        assert digest(base/f'spawn-revival-{host}.exe')==r['binary_sha256']
        for n,sha in r['link_inputs_sha256'].items():assert digest(ROOT/n)==sha,n
    for n,sha in build['production_sha256'].items():assert digest(ROOT/n)==sha,n
    prior=read(ROOT/'build/pride-grounded-latest.json');assert prior['result']=='PARTIAL' and prior['pre_fade_original_floor_contact_verified']
    for name,sha in prior['reports_sha256'].items():assert digest(old/name)==sha,name
    cpu=read(base/'ground-cpu-report.json');assert cpu['result']=='PASS' and len(cpu['cases'])==36
    baseline=read(base/'baseline-md-start/report.json',True)
    assert baseline['exit_code']==0 and baseline['presenter']=='native' and baseline['binary_sha256']==digest(old/'grounded-probe.exe')
    assert baseline['baseline'] and baseline['start_source']=='md' and not baseline['loaded_states'] and not baseline['guest_fixture_edits']
    assert [int(r['age']) for r in rows(base/'baseline-md-start/owner-events.csv') if r['event']=='normal']==[345]
    trace=rows(base/'baseline-md-start/start.csv');assert [(int(r['native']),int(r['selected'])) for r in trace[:2]]==[(64,65),(1248,1255)]
    raw=(base/'baseline-md-start/normal-wram.bin').read_bytes();assert struct.unpack_from('<HH',raw,0x1ffa4)==(65,1255)
    original=ROOT/'build/pride-default-death-reference/1400/fields.json'
    original_fields=json.loads(original.read_text());assert next(r for r in original_fields if r['frame']==3156)['xy']==[65,1255]
    assert next(r for r in original_fields if r['frame']==3202)['checkpoint']==0
    expected={int(r['age']):r for r in rows(ROOT/'build/pride-revival-scene/original-revival.csv') if r['checkpoint']=='0'}
    font_path=ROOT/'build/pride-default-actor/font-oracle/original-fonts.bin';raw=font_path.read_bytes();fonts={}
    assert raw[:8]==b'SNHUD002'
    for at in range(8,len(raw),1044):fonts[tuple(struct.unpack_from('<4I',raw,at))]=indices(raw[at+532:at+1044])
    def glyphs(folder):
        raw=(folder/'prepared-fonts.bin').read_bytes();assert raw[:8]==b'PRDHUD01' and (len(raw)-8)%1052==0;count=0
        for at in range(8,len(raw),1052):
            age,kind,maximum,current,initial,x,y=struct.unpack_from('<7I',raw,at)
            assert 274<=age<=300 and y==14 and x==(208 if kind else 16)
            assert (maximum,current)==((4,4) if kind else (16,0))
            key=(kind,maximum,current,initial)
            if kind:key=next(k for k in fonts if k[:3]==(1,4,4))
            assert raw[at+28:at+1052]==fonts[key],(folder,age,key);count+=1024
        return count
    def capture(folder,host):
        r=read(folder/'report.json',True)
        assert r['exit_code']==0 and r['host']==host and not r['baseline']
        assert not r['loaded_states'] and not r['guest_fixture_edits'] and r['presenter']=='owned'
        assert r['binary_sha256']==build['runs'][host]['binary_sha256'];return r
    def timing(folder,start,entry,last,neutral=True):
        events=rows(folder/'owner-events.csv');by={}
        for r in events:by.setdefault(r['event'],[]).append(r)
        assert [int(r['field']) for r in by['begin']]==[entry]
        for event,age in (('native_health',225),('native_actor',255),('default_idle_prepared',268),('default_ground_call',268),('default_ground_return',268),('default_idle_advanced',274)):
            assert [int(r['age']) for r in by[event]]==[age],(folder,event)
        assert int(by['default_ground_call'][0]['value'])==(1255 if start=='md' else 1248)
        assert int(by['default_ground_return'][0]['value'])==1255
        assert not by.get('checkpoint_hold_count')
        policy=rows(folder/'spawn-policy.csv');assert len(policy)==(5 if last>=entry+300 else 3)
        for r in policy:
            assert int(r['md'])==(start=='md') and r['checkpoint']=='0'
            assert (int(r['selected_x']),int(r['selected_y']))==((65,1255) if start=='md' else (64,1248))
            assert r['saved_x']==r['selected_x'] and r['saved_y']==r['selected_y']
        comparisons=policy[1:];assert [r['pc'] for r in comparisons]==['c087b5','c087bf','c0881d','c08827'][:len(comparisons)]
        assert all(int(r['selected_czn'])==3 and int(r['original_czn'])==(1 if start=='md' else 3) for r in comparisons)
        for r in rows(folder/'owner-fields.csv'):
            age=int(r['age']);assert int(r['native_health'])==(0 if age<274 else 4)
            if age>=268:
                assert int(r['y'])==1255
                if neutral or age<300:
                    assert int(r['x'])==(65 if start=='md' else 64)
                    assert int(r['draw_pose'],16)==int(expected[age]['snes_pose']) and int(r['raw_timer'])==int(expected[age]['timer'])
        if last>=entry+300:
            assert [int(r['age']) for r in by['normal']]==[300]
            assert len(by['hold_call'])==len(by['hold_return'])==32
            post=rows(folder/'post-ready.csv')
            if neutral:
                assert [int(r['timer']) for r in post]==[4,3,2,1,0,5,4,3,2][:len(post)]
                assert all(r['callback']=='c0ea93' and int(r['y'])==1255 for r in post)
        return policy
    def unchanged(folder,reference):
        old_capture=read(reference/'report.json',True)
        assert json.loads((folder/'report.json').read_text())['guest']==old_capture['guest']
        for file in ('route.ram','render-owned.rgb','prepared-fonts.bin','owner-events.csv','owner-fields.csv','post-ready.csv','picture.png'):
            if (reference/file).exists():assert digest(folder/file)==digest(reference/file),(folder,file)
    cases={};canonical={};compared=font_count=0
    for start in ('snes','md'):
        for width in (256,320):
            for graphics in ('native','frames','palette','all'):
                previous=None
                for mode in ('aot','lle'):
                    name=f'default/{start}-{width}-{graphics}-{mode}';folder=base/name;r=capture(folder,'probe')
                    timing(folder,start,1777 if start=='md' else 1776,3000)
                    identity=(r['guest'],digest(folder/'route.ram'))
                    if start not in canonical:canonical[start]=identity
                    assert canonical[start]==identity
                    rendered=rows(folder/'render-fields.csv');release=int(rendered[-1]['age'])
                    assert release==(301 if graphics=='all' else 302) and rendered[-1]['released']=='1' and rendered[-1]['native_pixel_mismatch']=='0'
                    assert {int(x['y']) for x in rendered if int(x['age'])>=277}=={200}
                    assert all(int(x['x'])-int(x['column'])==(65 if start=='md' else 64) for x in rendered if int(x['age'])>=277)
                    if start=='snes':unchanged(folder,old/f'default/{width}-{graphics}-{mode}');proof={'exact_predecessor_owned_fields':release+1}
                    else:proof=verify_default_pixels(folder,width,graphics in ('frames','all'),graphics in ('palette','all'),release+1);compared+=proof['pixels_compared']
                    font_count+=glyphs(folder)
                    trace=digest(folder/'render-owned.rgb')
                    if previous:assert previous==trace
                    previous=trace;cases[name]=dict(release_age=release,**proof)
                    print(name+' selected-default/timing/position/art PASS',flush=True)
    for width in (256,320):
        for graphics in ('native','all'):
            for mode in ('aot','lle'):
                folder=base/f'checkpoint/snes-{width}-{graphics}-{mode}';capture(folder,'probe');unchanged(folder,old/f'checkpoint/{width}-{graphics}-{mode}')
                policy=rows(folder/'spawn-policy.csv');assert all(r['checkpoint']=='1' and r['md']=='0' for r in policy)
                assert all(r['original_czn']==r['selected_czn'] for r in policy)
    alternate={};diagnostic_compared=0
    for width,graphics in ((256,'native'),(320,'all')):
        previous=None
        for mode in ('aot','lle'):
            folder=base/f'alternate/md-{width}-{graphics}-{mode}';r=capture(folder,'probe');timing(folder,'md',2029,2329,False)
            assert r['route']=='checkpoint' and all(x['checkpoint']=='0' for x in rows(folder/'spawn-policy.csv'))
            proof=verify_default_pixels(folder,width,graphics=='all',graphics=='all',301);diagnostic_compared+=proof['pixels_compared'];font_count+=glyphs(folder)
            state=(r['guest'],digest(folder/'render-owned.rgb'),digest(folder/'post-ready.csv'))
            if previous:assert previous==state
            previous=state
            alternate[folder.name]=dict(default_context_verified=True,pre_ready_position_verified=True,
                first_ready_observation=rows(folder/'post-ready.csv')[0],active_input_fidelity_verified=False)
    def pcm(folder,field):
        with wave.open(str(folder/'audio.wav'),'rb') as f:
            assert f.getframerate()==48000 and f.getnchannels()==2 and f.getnframes()==field*48000*357366//21477272
            return f.readframes(f.getnframes())
    clients=client_pixels=0;audio={}
    def window(folder,width,graphics,field,start,entry,default=True):
        nonlocal clients,client_pixels,font_count
        r=capture(folder,'sdl');w,h,client=pixels(folder/'window.png');assert (w,h)==(width*2,448)
        if default:
            timing(folder,start,entry,field,entry!=2029);font_count+=glyphs(folder)
            if field<entry+303:
                verify_default_pixels(folder,width,graphics in ('frames','all'),graphics in ('palette','all'),field-entry+1)
                raw=frame_records(folder/'render-owned.rgb',width)[field-entry][-width*224*4:];colors=array.array('I');colors.frombytes(raw)
                image=[((c>>16)&255,(c>>8)&255,c&255) for c in colors];rw=width
            else:
                rw,_,image=pixels(base/f'default/{start}-{width}-{graphics}-{r["execution"]}/picture.png')
                assert r['guest']==canonical[start][0]
        else:
            rw,_,image=pixels(base/f'checkpoint/snes-{width}-{graphics}-{r["execution"]}/picture.png')
        assert all(client[y*w+x]==image[(y//2)*rw+x//2] for y in range(h) for x in range(w))
        data=pcm(folder,field);key=start,field
        if key in audio:assert audio[key]==data
        audio[key]=data;clients+=1;client_pixels+=w*h
        return data
    specs=[(w,g,f) for w,g in ((256,'native'),(320,'all')) for f in (2054,2077,3000)]
    specs += [(w,g,2072) for w in (256,320) for g in ('frames','palette')]
    for width,graphics,field in specs:
        for mode in ('aot','lle'):window(base/f'windows/default-md-{width}-{graphics}-{mode}-{field}',width,graphics,field,'md',1777)
    for width,graphics,field in ((256,'native',2053),(320,'all',3000)):
        for mode in ('aot','lle'):
            folder=base/f'windows/default-snes-{width}-{graphics}-{mode}-{field}';data=window(folder,width,graphics,field,'snes',1776)
            assert data==pcm(old/f'windows/{width}-{graphics}-{mode}-{field}',field)
    for width,graphics,mode in ((256,'native','aot'),(320,'all','lle')):
        folder=base/f'windows/checkpoint-snes-{width}-{graphics}-{mode}-5400';data=window(folder,width,graphics,5400,'snes',0,False)
        assert data==pcm(old/f'windows/checkpoint-{width}-{graphics}-{mode}',5400)
        window(base/f'windows/alternate-md-{width}-{graphics}-{mode}-2329',width,graphics,2329,'md',2029)
    overlap=read(base/'overlap-windows/report.json');assert overlap['result']=='PASS'
    assert overlap['binary_sha256']==build['runs']['sdl']['binary_sha256']
    for name,r in overlap['runs'].items():
        folder=base/'overlap-windows'/name;field=int(name.split('-')[-1]);mode=name.split('-')[0]
        for file,sha in r['artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
        timing(folder,'md',1777,field);font_count+=glyphs(folder)
        w,h,client=pixels(folder/'window.png');assert (w,h)==(640,448)
        if field==2072:
            verify_default_pixels(folder,320,False,False,296)
            raw=frame_records(folder/'render-owned.rgb',320)[295][-320*224*4:];colors=array.array('I');colors.frombytes(raw)
            image=[((c>>16)&255,(c>>8)&255,c&255) for c in colors]
        else:
            _,_,image=pixels(base/f'default/md-320-native-{mode}/picture.png')
        assert pcm(folder,field)==audio['md',field]
        assert all(client[y*w+x]==image[(y//2)*320+x//2] for y in range(h) for x in range(w))
        clients+=1;client_pixels+=w*h
    active_base=base/'original-active-ready';active=read(active_base/'report.json')
    assert active['result']=='ORIGINAL_SOURCE_OBSERVED' and not active['loaded_states'] and not active['guest_edits']
    for label,r in active['runs'].items():
        assert r['prefix_controls']==14
        for file,sha in r['artifacts_sha256'].items():assert digest(active_base/label/file)==sha,(label,file)
        if label!='neutral':
            observed=json.loads((active_base/label/'fields.json').read_text())
            assert next(x['age'] for x in observed if x['xy'][0]!=65)==304
    for path in (Path(__file__),ROOT/'tools/verify_pride_default_actor_pixels.py',font_path,original,ROOT/'build/pride-revival-scene/original-revival.csv'):
        sources[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path)
    index=dict(result='PARTIAL',scope=__doc__,source_sha256=sources,reports_sha256=bound,default_cases=cases,
        independent_new_md_composed_pixels=compared,original_cpu_glyph_indices=font_count,actual_windows_clients=clients,checked_client_pixels=client_pixels,
        native_default_regression_cases=16,native_checkpoint_regression_cases=8,alternate_md_context_diagnostics=alternate,
        diagnostic_alternate_composed_pixels=diagnostic_compared,neutral_windows_clients=clients-2,active_input_diagnostic_windows_clients=2,
        original_md_late_right_first_motion_age=304,matched_port_input_schedule_verified=False,active_ready_input_handoff_verified=False,
        original_floor_contact_cases=36,selected_default_comparisons=4,independent_default_start_sources_verified=True,
        md_start_checkpoint_revival_verified=False,broader_gameplay_initialization_profiles_verified=False,
        native_actor_reset_age=255,original_md_actor_reset_age=254,default_save_lifecycle_verified=False,
        final_repeated_contexts_verified=False,production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-spawn-revival-latest.json').write_text(json.dumps(index,indent=2)+'\n')
    print('Independent default start/revival comparisons/windows verified; MD-start checkpoint and full Pride remain open',flush=True)


if __name__=='__main__':main()
