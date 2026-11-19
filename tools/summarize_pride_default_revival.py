"""Verify default revival clock integration; expose missing actor/presenter preparation."""
import json
from pathlib import Path
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-default-revival';reports={}
    def read(name):
        path=base/name;value=json.loads(path.read_text())
        for n,sha in value.get('source_sha256',{}).items():assert digest(ROOT/n)==sha,n
        reports[name]=digest(path);return value
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/f'default-revival-{host}.exe')==run['binary_sha256']
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
    def timing(name):
        folder=base/name;events=rows(folder/'owner-events.csv');fields=rows(folder/'owner-fields.csv')
        restore=rows(folder/'restore-events.csv');by={}
        for r in events:by.setdefault(r['event'],[]).append(r)
        assert len(by['begin'])==len(by['normal'])==1
        start=int(by['begin'][0]['field']);assert start==1776
        assert [int(r['age']) for r in fields]==list(range(301))
        assert [int(r['field']) for r in fields]==list(range(start,start+301))
        assert int(by['native_health'][0]['age'])==225 and int(by['normal'][0]['age'])==300
        assert int(by['normal_release'][0]['age'])==300
        assert len(by['hold_call'])==len(by['hold_return'])==32
        assert not by.get('checkpoint_hold_count') and not by.get('retain_first_hold_pose')
        assert all(int(r['native_health'])==(0 if int(r['age'])<274 else 4) for r in fields)
        assert [int(r['age']) for r in restore if r['event']=='publish']==[274]
        assert all(int(r['age'])==225 for r in restore if r['event'] in ('request_health','request_roar'))
        assert all(int(r['roar'])==0 for r in rows(folder/'restore-fields.csv') if 225<=int(r['age'])<=300)
        decoded=rows(folder/'decompress.csv');assert sum(r['event']=='prepared' for r in decoded)==7
        before=(folder/'before-wram.bin').read_bytes()
        # The reload marker becomes1 even on the no-checkpoint path. The
        # saved native spawn still equals the source-ROM default coordinates.
        native=(ROOT/'Lion King, The (USA).sfc').read_bytes()
        assert struct.unpack_from('<H',before,0x1ffa2)[0]==1
        assert before[0x1ffa4:0x1ffa8]==native[0x39d:0x3a1]
        actor=int(by['native_actor'][0]['age'])
        mismatch=[int(r['age']) for r in fields if int(r['age']) in expected and
                  (int(r['draw_pose'],16)!=int(expected[int(r['age'])]['snes_pose']) or
                   int(r['raw_timer'])!=int(expected[int(r['age'])]['timer']))]
        assert actor==255 and mismatch  # Retain observed incomplete fidelity.
        return dict(start=start,health_age=274,normal_age=300,native_actor_age=actor,original_md_actor_age=254,
                    original_idle_mismatch_ages=mismatch,balanced_wait_calls=32)
    defaults={};reference_guest=None
    for width in (256,320):
        for graphics in ('native','all'):
            previous=None
            for mode in ('aot','lle'):
                name=f'default/{width}-{graphics}-{mode}';r=capture(name)
                assert r['presenter']=='native' and r['route']=='default' and r['frames']==3000
                info=timing(name);defaults[name]=info
                if reference_guest is None:reference_guest=r['guest']
                assert r['guest']==reference_guest
                tracked=digest(base/name/'route.ram')
                if previous:assert previous==tracked
                previous=tracked
                if width==256 and graphics=='native' and mode=='aot':canonical_ram=tracked
                assert tracked==canonical_ram
    checkpoint_guest=hashes(ROOT/'build/pride-compiled-revival/sync-full-headless/lle/run.log')
    checkpoint_cases=0
    for width in (256,320):
        for graphics in ('native','all'):
            for mode in ('aot','lle'):
                name=f'checkpoint/{width}-{graphics}-{mode}';r=capture(name)
                assert r['presenter']=='owned' and r['route']=='checkpoint' and r['frames']==5400
                assert r['guest']==checkpoint_guest
                reference=ROOT/f'build/pride-compiled-prepared/headless-{width}-{mode}/{graphics}-owned'
                for file in ('route.ram','render-owned.rgb','prepared-fonts.bin','prepared-objects.csv'):
                    assert digest(base/name/file)==digest(reference/file),(name,file)
                checkpoint_cases+=1
    def pcm(folder,fields):
        with wave.open(str(folder/'audio.wav'),'rb') as wav:
            assert wav.getframerate()==48000 and wav.getnchannels()==2
            assert wav.getnframes()==fields*48000*357366//21477272
            return wav.readframes(wav.getnframes())
    client_pixels=0;audio={};windows=0
    for width,graphics in ((256,'native'),(320,'all')):
        for field in (2076,3000):
            previous=None
            for mode in ('aot','lle'):
                name=f'windows/{width}-{graphics}-{mode}-{field}';r=capture(name,'sdl')
                assert r['presenter']=='native' and r['frames']==field
                timing(name)
                window=pixels(base/name/'window.png');assert window[:2]==(2*width,448)
                current=(r['guest'],window)
                if previous:assert previous==current
                previous=current;client_pixels+=window[0]*window[1];windows+=1
                data=pcm(base/name,field)
                if field in audio:assert audio[field]==data
                audio[field]=data
                if field==3000:assert r['guest']==reference_guest
    with wave.open(str(ROOT/'build/pride-compiled-revival/sync-audio/lle/audio.wav'),'rb') as wav:
        checkpoint_pcm=wav.readframes(wav.getnframes())
    for width,graphics,mode in ((256,'native','aot'),(320,'all','lle')):
        name=f'windows/checkpoint-{width}-{graphics}-{mode}';r=capture(name,'sdl')
        assert r['guest']==checkpoint_guest and pcm(base/name,5400)==checkpoint_pcm
        # The SDL client is an exact 2x expansion of the independently bound
        # headless final image, with no overlay in these ordinary captures.
        w,h,client=pixels(base/name/'window.png')
        rw,rh,reference=pixels(base/f'checkpoint/{width}-{graphics}-{mode}/picture.png')
        assert (w,h)==(rw*2,rh*2)
        assert all(client[y*w+x]==reference[(y//2)*rw+x//2] for y in range(h) for x in range(w))
        client_pixels+=w*h;windows+=1
    limit=capture('owned-default-limit',exit_code=75)
    assert limit['presenter']=='owned'
    assert 'default prepared batch unavailable age=274 count=0' in (base/'owned-default-limit/run.log').read_text()
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={**{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in original_sources.values()},
                      'tools/summarize_pride_default_revival.py':digest(Path(__file__)),
                      str(oracle.relative_to(ROOT)).replace('\\','/'):digest(oracle),
                      str(md_reference.relative_to(ROOT)).replace('\\','/'):digest(md_reference)},
        default_clock_cases=len(defaults),default_clock_details=defaults,checkpoint_regression_cases=checkpoint_cases,
        actual_windows_clients=windows,paired_client_pixels=client_pixels,
        default_pcm_bytes=len(audio[3000]),checkpoint_pcm_bytes=len(checkpoint_pcm),
        default_health_and_ready_clock_verified=True,default_original_actor_preparation_verified=False,
        default_owned_renderer_verified=False,default_owned_rejection_exit=75,
        default_actual_saves_verified=False,final_life_and_repeated_death_verified=False,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-default-revival-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Default health/ready clock and checkpoint regressions verified; default actor/render preparation remains open',flush=True)


if __name__=='__main__':main()
