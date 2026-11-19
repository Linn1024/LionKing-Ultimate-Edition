"""Bind native default initializer, owned composition and native handoff; full Pride stays open."""
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows
from verify_windows import hashes,pixels
from probe_pride_prepared_state import frame_records
from verify_pride_default_actor_pixels import verify_default_pixels
from verify_pride_prepared_current_fonts import indices
import array


def main():
    base=ROOT/'build/pride-default-actor';reports={}
    def read(name):
        path=base/name;value=json.loads(path.read_text())
        for n,sha in value.get('source_sha256',{}).items():assert digest(ROOT/n)==sha,n
        reports[name]=digest(path);return value
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/f'default-actor-{host}.exe')==run['binary_sha256']
        for n,sha in run['link_inputs_sha256'].items():assert digest(ROOT/n)==sha,n
    for n,sha in build['production_sha256'].items():assert digest(ROOT/n)==sha,n
    def capture(name,host='probe',exit_code=0):
        r=read(name+'/report.json');assert r['exit_code']==exit_code and r['host']==host
        assert r['binary_sha256']==build['runs'][host]['binary_sha256']
        assert not r['loaded_states'] and not r['guest_fixture_edits']
        for n,sha in r['artifacts_sha256'].items():assert digest(base/name/n)==sha,(name,n)
        return r
    oracle=ROOT/'build/pride-revival-scene/original-revival.csv'
    expected={int(r['age']):r for r in rows(oracle) if r['checkpoint']=='0'}
    md_reference=ROOT/'build/pride-default-death-reference/report.json'
    md=json.loads(md_reference.read_text());assert md['result']=='PASS'
    prefix=md['selected_prefix_fields']
    original_sources={
        'script':ROOT/'tools/pride_default_death_reference.py',
        'trace_source':ROOT/'tools/md_revival_trace.c',
        'trace_dll':ROOT/'build/md_revival_trace.dll',
        'core':ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
        'input':ROOT/'build/md-next-levels-replay/frames.json',
        'fields':ROOT/f'build/pride-default-death-reference/{prefix}/fields.json',
        'callbacks':ROOT/f'build/pride-default-death-reference/{prefix}/callbacks.csv'}
    for name,path in original_sources.items():assert digest(path)==md['source_sha256'][name],name
    boundaries=md['case'];zero=boundaries['death']
    assert boundaries['health_restored']-zero==274 and boundaries['normal_play_jump'][0]-zero==300
    assert boundaries['new_actor_owner'][0]-zero==254 and not boundaries['respawn_hold_iterations']
    original_fields={r['frame']-zero:r for r in json.loads(original_sources['fields'].read_text())}
    for age,row in expected.items():
        assert int(row['md_pose'])==original_fields[age]['pose']
        assert int(row['timer'])==original_fields[age]['words'][13]>>8
    generation=read('generation-report.json');assert generation['original_analysis_manifest_exact']
    assert {0xc087bf,0xc087c5,0xc087eb,0xc087fe}<=set(generation['hook_pcs'])
    assert {0xc087c1,0xc087e8,0xc087f6}<=set(generation['redirect_pcs'])
    for n,sha in generation['generated_sha256'].items():assert digest(base/'generated'/n)==sha,n
    gpu=read('original-sat/gpu-report.json');assert gpu['result']=='PASS'
    assert gpu['death_fields']==248 and gpu['revival_and_normal_fields']==44 and gpu['normal_play_pose_delay']==1
    sat=read('original-sat/report.json');assert sat['result']=='PASS'
    for name,sha in sat['artifacts_sha256'].items():assert digest(base/'original-sat'/name)==sha,name
    font_report=read('font-oracle/report.json');assert font_report['result']=='PASS'
    assert font_report['original_roar_cases']==8436 and font_report['transition_flags']==[0,1,2,65535]
    for n,sha in font_report['artifacts_sha256'].items():assert digest(base/'font-oracle'/n)==sha,n
    for n,sha in font_report['link_inputs_sha256'].items():assert digest(ROOT/n)==sha,n
    original_oracle=json.loads((ROOT/'build/pride-native-hud-current/report.json').read_text())
    assert original_oracle['probe_sha256']==digest(ROOT/'engine/build-win/tlk_native_hud_oracle.exe')
    raw=(base/'font-oracle/original-fonts.bin').read_bytes();fonts={}
    assert raw[:8]==b'SNHUD002'
    for at in range(8,len(raw),1044):
        key=tuple(struct.unpack_from('<5I',raw,at)[:4]);fonts[key]=indices(raw[at+532:at+1044])
    def timing(folder,last):
        events=rows(folder/'owner-events.csv');fields=rows(folder/'owner-fields.csv');by={}
        for r in events:by.setdefault(r['event'],[]).append(r)
        assert len(by['begin'])==1 and int(by['begin'][0]['field'])==1776
        assert [int(r['age']) for r in fields]==list(range(min(last-1776,300)+1))
        assert int(by['native_health'][0]['age'])==225
        assert int(by['native_actor'][0]['age'])==255
        assert [int(r['age']) for r in by['default_idle_prepared']]==[268]
        assert [int(r['value']) for r in by['default_idle_prepared']]==[5]
        for event in ('default_idle_advance_call','default_idle_advanced','default_idle_advance_return'):
            assert [int(r['age']) for r in by[event]]==[274]
        assert int(by['default_idle_advanced'][0]['value'])==4
        assert not by.get('checkpoint_hold_count')
        for r in fields:
            age=int(r['age']);assert int(r['native_health'])==(0 if age<274 else 4)
            if age>=268:
                assert int(r['draw_pose'],16)==int(expected[age]['snes_pose'])
                assert int(r['raw_timer'])==int(expected[age]['timer'])
        if last>=2076:
            assert [int(r['age']) for r in by['normal']]==[300]
            assert len(by['hold_call'])==len(by['hold_return'])==32
            restore=rows(folder/'restore-events.csv')
            assert sum(r['event']=='retain_default_idle_callback' for r in restore)==1
            post=rows(folder/'post-ready.csv');limit=min(last-1776,308)
            assert [int(r['elapsed']) for r in post]==list(range(300,limit+1))
            assert [int(r['timer']) for r in post]==[4,3,2,1,0,5,4,3,2][:len(post)]
            assert all(r['callback']=='c0ea93' for r in post)
        return by
    def glyphs(folder):
        raw=(folder/'prepared-fonts.bin').read_bytes();assert raw[:8]==b'PRDHUD01' and (len(raw)-8)%1052==0
        total=0
        for at in range(8,len(raw),1052):
            age,kind,maximum,current,initial,x,y=struct.unpack_from('<7I',raw,at)
            assert 274<=age<=300 and y==14 and x==(208 if kind else 16)
            assert maximum==(4 if kind else 16) and current==(4 if kind else 0)
            key=(kind,maximum,current,initial)
            if kind:key=(1,4,4,next(k[3] for k in fonts if k[:3]==(1,4,4)))
            assert raw[at+28:at+1052]==fonts[key],(folder,age,key)
            total+=1024
        return total
    cases={};canonical_guest=None;canonical_ram=None;compared=glyph_count=0
    for width in (256,320):
        for graphics in ('native','frames','palette','all'):
            previous=None
            for mode in ('aot','lle'):
                name=f'default/{width}-{graphics}-{mode}';r=capture(name);folder=base/name
                assert r['presenter']=='owned' and r['frames']==3000 and r['route']=='default'
                timing(folder,3000)
                if canonical_guest is None:canonical_guest=r['guest'];canonical_ram=digest(folder/'route.ram')
                assert r['guest']==canonical_guest and digest(folder/'route.ram')==canonical_ram
                rendered=rows(folder/'render-fields.csv');release=int(rendered[-1]['age'])
                assert release in (300,301,302) and rendered[-1]['released']=='1' and rendered[-1]['native_pixel_mismatch']=='0'
                proof=verify_default_pixels(folder,width,graphics in ('frames','all'),graphics in ('palette','all'),release+1)
                compared+=proof['pixels_compared'];glyph_count+=glyphs(folder)
                if release==302:
                    final=frame_records(folder/'render-owned.rgb',width)[302][-width*224*4:]
                    assert final==(folder/'native-302.rgb').read_bytes()
                identity=tuple(digest(folder/file) for file in ('render-owned.rgb','prepared-fonts.bin','post-ready.csv'))
                if previous:assert previous==identity,(name,'mode trace')
                previous=identity;cases[name]=dict(release_age=release,original_cpu_idle_fields_exact=33,**proof)
                print('Default composition/glyph/idle checks '+name+' PASS',flush=True)
    checkpoint_guest=hashes(ROOT/'build/pride-compiled-revival/sync-full-headless/lle/run.log')
    for width in (256,320):
        for graphics in ('native','all'):
            for mode in ('aot','lle'):
                name=f'checkpoint/{width}-{graphics}-{mode}';r=capture(name)
                assert r['guest']==checkpoint_guest and r['frames']==5400
                reference=ROOT/f'build/pride-compiled-prepared/headless-{width}-{mode}/{graphics}-owned'
                for file in ('route.ram','prepared-fonts.bin','prepared-objects.csv'):
                    assert digest(base/name/file)==digest(reference/file),(name,file)
                before=frame_records(reference/'render-owned.rgb',width);after=frame_records(base/name/'render-owned.rgb',width)
                assert before.keys()==after.keys()
                plane=width*224*4
                for age,a in after.items():
                    b=before[age]
                    assert a[:56+plane]==b[:56+plane] and a[-plane:]==b[-plane:],(name,age)
                    new=array.array('I');new.frombytes(a[56+plane:56+2*plane])
                    old=array.array('I');old.frombytes(b[56+plane:56+2*plane])
                    assert all((x&0xffffff)==(y&0xffffff) and (x|y)==x for x,y in zip(new,old)),(name,age,'occlusion tags')
    def pcm(folder,field):
        with wave.open(str(folder/'audio.wav'),'rb') as wav:
            assert wav.getframerate()==48000 and wav.getnchannels()==2
            assert wav.getnframes()==field*48000*357366//21477272
            return wav.readframes(wav.getnframes())
    window_cases=[(w,g,f) for w,g in ((256,'native'),(320,'all')) for f in (2053,2076,3000)]
    window_cases += [(w,g,2071) for w in (256,320) for g in ('frames','palette')]
    clients=client_pixels=0;audio={}
    for width,graphics,field in window_cases:
        previous=None
        for mode in ('aot','lle'):
            name=f'windows/{width}-{graphics}-{mode}-{field}';r=capture(name,'sdl');folder=base/name
            assert r['frames']==field and r['presenter']=='owned';timing(folder,field)
            w,h,client=pixels(folder/'window.png');assert (w,h)==(width*2,448)
            if field<2078:
                # SDL defaults to edge HUD placement; headless retains native
                # placement. Reconstruct this actual host's trace with the
                # independent art/palette oracle before checking its client.
                verify_default_pixels(folder,width,graphics in ('frames','all'),graphics in ('palette','all'),field-1776+1)
                record=frame_records(folder/'render-owned.rgb',width)[field-1776]
                colors=array.array('I');colors.frombytes(record[-width*224*4:])
                assert all(client[y*w+x]==((colors[(y//2)*width+x//2]>>16)&255,(colors[(y//2)*width+x//2]>>8)&255,colors[(y//2)*width+x//2]&255) for y in range(h) for x in range(w))
            else:
                rw,rh,image=pixels(base/f'default/{width}-{graphics}-{mode}/picture.png')
                assert all(client[y*w+x]==image[(y//2)*rw+x//2] for y in range(h) for x in range(w))
                assert r['guest']==canonical_guest
            glyph_count+=glyphs(folder)
            current=(r['guest'],(w,h,client))
            if previous:assert previous==current
            previous=current;clients+=1;client_pixels+=w*h
            data=pcm(folder,field)
            if field in audio:assert audio[field]==data
            audio[field]=data
    with wave.open(str(ROOT/'build/pride-compiled-revival/sync-audio/lle/audio.wav'),'rb') as wav:
        checkpoint_pcm=wav.readframes(wav.getnframes())
    for width,graphics,mode in ((256,'native','aot'),(320,'all','lle')):
        name=f'windows/checkpoint-{width}-{graphics}-{mode}';r=capture(name,'sdl');folder=base/name
        assert r['guest']==checkpoint_guest and pcm(folder,5400)==checkpoint_pcm
        w,h,client=pixels(folder/'window.png');rw,rh,image=pixels(base/f'checkpoint/{width}-{graphics}-{mode}/picture.png')
        assert (w,h)==(rw*2,rh*2) and all(client[y*w+x]==image[(y//2)*rw+x//2] for y in range(h) for x in range(w))
        clients+=1;client_pixels+=w*h
    overlap=read('overlap-windows/report.json');assert overlap['result']=='PASS'
    assert overlap['binary_sha256']==build['runs']['sdl']['binary_sha256']
    for name,r in overlap['runs'].items():
        assert r['exit_code']==0
        for n,sha in r['artifacts_sha256'].items():assert digest(base/'overlap-windows'/name/n)==sha,n
        clients+=1;client_pixels+=r['client_pixels']
    sources=[Path(__file__),ROOT/'tools/verify_pride_default_actor_pixels.py',ROOT/'tools/probe_pride_scene_render.py',
             ROOT/'tools/verify_pride_prepared_current_fonts.py',oracle,md_reference,
             ROOT/'build/pride-death-controller/original-fields.csv',ROOT/'build/pride-death-controller/original-palettes.csv',
             ROOT/'build/pride-owned-death-art/original-bitmaps.bin',ROOT/'build/pride-owned-revival-art/original-bitmaps.bin']
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={**{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in original_sources.values()},
                      **{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}},
        default_owned_cases=cases,default_composed_pixels=compared,original_cpu_installed_glyph_indices=glyph_count,
        checkpoint_regression_cases=8,checkpoint_composed_pixels_unchanged=True,checkpoint_occlusion_tags_extended=True,
        actual_windows_clients=clients,checked_client_pixels=client_pixels,
        default_pcm_bytes=len(audio[3000]),checkpoint_pcm_bytes=len(checkpoint_pcm),
        original_default_idle_from_268_verified=True,native_ready_handoff_verified=True,
        native_actor_reset_age=255,original_md_actor_reset_age=254,original_default_scene_gpu_verified=True,
        original_normal_play_pose_delay=1,native_normal_gpu_phase_matched_to_md=False,
        broader_gameplay_initialization_profiles_verified=False,default_save_lifecycle_verified=False,
        final_repeated_contexts_verified=False,production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-default-actor-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Default native initializer/owned art/widgets/window/handoff verified; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
