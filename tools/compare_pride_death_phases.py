"""Relate native opcode observations to actual post-video-field death state."""
import hashlib
import json
import struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_death_phases import parse as phase_parse
from compare_pride_death_timeline import parse,expected
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-death-phases';source=out/'report.json'
    capture=json.loads(source.read_text());assert capture['result']=='PASS'
    assert capture['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
    assert capture['source_sha256']['script']==digest(ROOT/'tools/pride_death_phases.py')
    assert capture['source_sha256']['input']==digest(ROOT/'build/pride-health-death-native/neutral-tail.polled.tape')
    reload_source=ROOT/'build/pride-death-reload/report.json'
    reload=json.loads(reload_source.read_text());assert reload['result']=='PASS'
    assert reload['headless_sha256']==capture['headless_sha256']
    assert reload['source_sha256']['earlier']==digest(source)
    assert reload['source_sha256']['script']==digest(ROOT/'tools/pride_death_reload.py')
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    tokens,_=parse(rom,0xebec,True)
    bank_sha='f42fc9fa3745e53e1953237e0a3b9fa78369c59511da30b2c74f02343c58c1bb'
    sources={}
    for name,run in capture['runs'].items():
        sampled={}
        for mode in ('aot','lle'):
            folder=out/(name+'-'+mode)
            assert hashes(folder/'run.log')==run['guest'] and digest(folder/'route.ram')==run['tracked_sha256']
            values=[]
            late_folder=ROOT/'build/pride-death-reload'/(name+'-'+mode)
            late=reload['runs'][name]
            assert hashes(late_folder/'run.log')==late['guest'] and digest(late_folder/'route.ram')==late['tracked_sha256']
            for frame,sha in zip(range(4400,5401),run['sampled_wram_hashes']+late['sampled_wram_hashes'],strict=True):
                file=(folder if frame<=4900 else late_folder)/f'hl_wram_{frame}.bin';assert digest(file)==sha
                ram=file.read_bytes();assert len(ram)==0x20000
                word=lambda a:struct.unpack_from('<H',ram,a)[0]
                draw=word(0xb21f)
                values.append({'frame':frame,'health':word(0x2004),'lives':word(0x1ffaa),
                               'pose':int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff,
                               'timer':word(0xb22d),'cursor':int.from_bytes(ram[0xb225:0xb228],'little'),
                               'xy':[word(0xb21b),word(0xb21d)],'camera':[word(0x4a),word(0x4c)],
                               'state_marker':int.from_bytes(ram[0xb243:0xb246],'little'),
                               'bank_ready':hashlib.sha256(ram[0x10000:0x10000+17792]).hexdigest()==bank_sha})
            sampled[mode]=values
        assert sampled['aot']==sampled['lle']
        assert phase_parse(out/(name+'-lle')/'run.log')==run['deaths']
        rows=sampled['lle'];by_frame={r['frame']:r for r in rows}
        death=next(r['frame'] for i,r in enumerate(rows) if i and not r['health'] and rows[i-1]['health'])
        active=next(r['frame'] for r in rows if death<r['frame']<death+100 and r['timer']==2)-1
        assert active-death==64
        for offset,(index,pose,timer) in enumerate(expected(tokens,280)):
            row=by_frame[active+offset]
            assert (row['pose'],row['timer'],row['cursor'])==(pose&0x3fffff,timer,0xc0ebec+(index+1)*4)
        bank=next(r['frame'] for r in rows if r['frame']>=death and r['bank_ready'])
        placement=next(r for r in rows if death<r['frame']<active and r['xy']!=by_frame[death]['xy'])
        assert placement['xy']==[(placement['camera'][0]+128)&65535,(placement['camera'][1]+112)&65535]
        assert all(by_frame[f]['xy']==placement['xy'] for f in range(placement['frame'],active+280))
        end=active+280;assert by_frame[end]['health'] and by_frame[end]['lives']==by_frame[death]['lives']-1
        cleared=next(r['frame'] for r in rows if r['frame']>=end and r['state_marker']==0)
        ready=next(r['frame'] for r in rows if r['frame']>=end and r['state_marker']==0xc32b24)
        observations=run['deaths'][0]['completed_opcode_fields']
        assert observations['entry']==[death-1] and observations['restore_health']==[end-1]
        # The raw call labels are retained as observations. Only snapshot
        # timers/cursors above prove the video clock; no +1 correction is
        # applied indiscriminately across resumed cooperative waits.
        signature={'health_zero_field':death,'complete_bank_field':bank,'placement_field':placement['frame'],
                   'stream_start_field':active,'extra_first_pose_hold_fields':active-death,
                   'stream_fields':280,'positive_health_field':end,'native_spare_decrement_field':end,
                   'old_actor_state_marker_cleared_field':cleared,'normal_state_marker_present_field':ready,
                   'health_restore_to_normal_state_marker_fields':ready-end}
        sources[name]=signature
    assert all(v==sources['native'] for v in sources.values()),sources
    md_source=ROOT/'build/pride-death-presentation-md/report.json'
    md=json.loads(md_source.read_text());assert md['result']=='PASS'
    assert md['source_sha256']['timeline']==digest(ROOT/'build/pride-death-timeline/report.json')
    assert md['source_sha256']['fields']==digest(ROOT/'build/pride-death-presentation-md/fields.json')
    result={'result':'SOUND_SOURCE_INDEPENDENT_NATIVE_PHASES_MD_PRESENTATION_OPEN','scope':__doc__,
            'headless_sha256':capture['headless_sha256'],'native_music_source_runs':8,'native_reload_source_runs':8,
            'per_source_aot_lle_full_wram_equal_fields':1001,'native_music_source_phase_signatures':sources,
            'all_music_sources_full_wram_identical':all(r['sampled_wram_hashes']==capture['runs']['native']['sampled_wram_hashes'] for r in capture['runs'].values()) and
                all(r['sampled_wram_hashes']==reload['runs']['native']['sampled_wram_hashes'] for r in reload['runs'].values()),
            'raw_opcode_call_labels_are_not_video_field_clock':True,
            'md_presentation_control_fields':md['sampled_video_fields'],
            'production_death_source_enabled':False,'full_first_level_fidelity_complete':False,
            'source_sha256':{'analysis':digest(Path(__file__)),'capture':digest(source),'reload_capture':digest(reload_source),'md_presentation':digest(md_source)}}
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print('All4 music sources: native death/reload phases identical,1001 complete WRAM fields AOT/LLE equal each PASS',flush=True)
    print(json.dumps(sources['native']),flush=True)


if __name__=='__main__':main()
