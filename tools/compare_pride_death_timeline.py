"""Audit original cub death streams, live clocks and scene staging.

Stream equality is bounded separately from the differing freeze/display/reload
phases. No production death-behavior source is enabled by this report.
"""
import csv
import hashlib
import json
import importlib.util
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import bitmap,snes_frame,md_frame


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(rom,start,native):
    rows=[]
    for i in range(128):
        at=start+i*4;duration=rom[at]
        pose=int.from_bytes(rom[at+1:at+4],'little' if native else 'big')
        if duration==255:
            if native:pose&=0x3fffff
            assert start<=pose<at and (pose-start)%4==0
            return rows,(pose-start)//4
        assert duration<128
        rows.append({'duration':duration,'pose':pose})
    raise AssertionError('Unbounded original animation stream')


def expected(tokens,ticks):
    result=[]
    for index,token in enumerate(tokens):
        for timer in range(token['duration'],-1,-1):
            result.append((index,token['pose'],timer))
            if len(result)==ticks:return result
    assert len(result)==ticks
    return result


def native_cases(folder,tokens):
    report_path=folder/'report.json';report=json.loads(report_path.read_text())
    assert report['result']=='PASS' and report['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
    rows=json.loads((folder/'samples.json').read_text());by_frame={r['frame']:r for r in rows}
    deaths=[r for i,r in enumerate(rows) if i and r['health']==0 and rows[i-1]['health']>0 and r['descriptor'] in (0x387,0x80d)]
    result=[]
    for death in deaths:
        start=death['frame']
        # First decrement after the first-frame freeze determines the active
        # stream clock; do not guess it from an absolute cross-console frame.
        decreased=next(r['frame'] for r in rows if r['frame']>=start and r['frame']<start+100 and r['words'][13]==tokens[0]['duration']-1)
        active=decreased-1
        assert active-start==64,(folder.name,start,active)
        for offset,(index,pose,timer) in enumerate(expected(tokens,280)):
            row=by_frame[active+offset];w=row['words']
            assert row['pose']==(pose&0x3fffff) and w[13]==timer,(folder.name,row['frame'],index,hex(row['pose']),timer,w[13])
            assert (w[9]|(w[10]&255)<<16)==0xc0ebec+(index+1)*4
            assert not row['skip_display_flag']
        placement=next(r for r in rows if start<r['frame']<active and r['xy']!=death['xy'])
        assert placement['xy']==[(placement['camera'][0]+128)&65535,(placement['camera'][1]+112)&65535]
        assert all(by_frame[f]['xy']==placement['xy'] for f in range(placement['frame'],active+280))
        end=by_frame[active+280]
        if death['lives']:
            assert end['health']>0 and end['lives']==death['lives']-1
        else:assert end['descriptor']==0x57b and end['health']==end['lives']==0
        result.append({'death':start,'spares_at_death':death['lives'],'active_clock_start':active,
                       'first_pose_extra_hold_fields':active-start,'animation_fields_verified':280,
                       'teleport_field':placement['frame'],'teleport_offset':[128,112],
                       'after_display_field':active+280,'final_life_also_plays_display':not death['lives']})
    assert result
    return result


def main():
    out=ROOT/'build/pride-death-timeline';report_path=out/'report.json'
    report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    # The MD object points at a10-byte animation descriptor, not directly at
    # the four-byte token stream. Do not decode descriptor bytes as opcodes.
    assert int.from_bytes(m[0x7e568:0x7e56c],'big')==0x7e5b2
    a,al=parse(s,0xc0ebec&0x3fffff,True)
    # Native token loop pointers include the C0 bank whereas this ROM offset
    # parser uses bounded offsets. Resolve that bank before normalizing.
    b,bl=parse(m,0x7e5b2,False)
    assert len(a)==len(b)==33 and al==bl==32
    assert [x['duration'] for x in a]==[x['duration'] for x in b]
    spec=importlib.util.spec_from_file_location('death_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    bank,compressed=lz.decompress(s,0xdfa78c)
    work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:0x3f0000+len(bank)]=bank
    raw=(out/'native/lle/hl_wram_4498.bin').read_bytes()
    assert bank==raw[0x10000:0x10000+len(bank)],'Original death-loader bank differs'
    art=[]
    for i,(left,right) in enumerate(zip(a,b)):
        one=bitmap(work,snes_frame(work,left['pose']&0x3fffff),False,with_origin=True)
        two=bitmap(m,md_frame(m,right['pose']),True,with_origin=True)
        assert one==two,('Original death art differs',i,hex(left['pose']),hex(right['pose']))
        art.append({'index':i,'duration':left['duration'],'native_pose':hex(left['pose']),'md_pose':hex(right['pose']),
                    'origin':list(one[:2]),'size':list(one[2:4]),'anchored_indexed_sha256':hashlib.sha256(one[4]).hexdigest()})
    checkpoint=native_cases(out/'native',a);continuing=native_cases(out/'native-continue',a)
    assert len(checkpoint)==1 and len(continuing)==3
    md_report=json.loads((out/'md/report.json').read_text());assert md_report['result']=='PASS'
    rows=json.loads((out/'md/samples.json').read_text());by_frame={r['frame']:r for r in rows}
    events=list(csv.DictReader((out/'md/callbacks.csv').open()))
    deaths=[r for r in events if r['pc']=='1d6cb2'];assert len(deaths)==9
    md_cases=[]
    for number,death in enumerate(deaths):
        start=int(death['frame']);stop=int(deaths[number+1]['frame']) if number+1<len(deaths) else 15301
        loops=[r for r in events if r['pc']=='1d6da0' and start<=int(r['frame'])<stop]
        if number==8:
            assert not loops
            md_cases.append({'death':start,'remaining_total':0,'display_skipped':True})
            continue
        assert [int(r['d7']) for r in loops]==list(range(200,-1,-1))
        loop_start=int(loops[0]['frame']);loop_end=int(loops[-1]['frame'])+1
        assert loop_start-start==24 and loop_end-loop_start==201
        for offset,(index,pose,timer) in enumerate(expected(b,225)):
            row=by_frame[start+offset];w=row['words']
            assert row['pose']==pose and w[13]>>8==timer,(number,row['frame'],index,hex(row['pose']),timer,w[13])
            assert (w[9]<<16|w[10])==0x7e5b2+(index+1)*4
        afters=[r for r in events if r['pc']=='1d6dee' and start<=int(r['frame'])<stop]
        assert len(afters)==201
        for before,after in zip(loops,afters):
            for axis,target in (('x',160),('y',128)):
                position=int(before[axis]);camera=int(before['camera_'+axis]);delta=(position-camera)&65535
                delta=delta if delta<32768 else delta-65536
                wanted=(position+(delta<target)-(delta>target))&65535
                assert int(after[axis])==wanted,(number,before,after,axis,wanted)
        restored=next(r['frame'] for r in rows if loop_end<=r['frame']<stop and r['health']>0)
        assert restored-loop_end==45 and restored-start==270
        md_cases.append({'death':start,'display_skipped':False,'loop_start':loop_start,'loop_end':loop_end,
                         'main_loop_fields':201,'animated_fields_including_fade':225,'first_pose_extra_hold_fields':0,
                         'centering_steps_verified':201,'target_screen_offset':[160,128],
                         'health_restored':restored,'post_loop_to_health_restore_fields':45})
    report={'result':'STREAMS_EQUAL_STAGING_DIFFERENT_ADAPTER_OPEN','scope':__doc__,
            'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'death_stream_tokens':33,'loop_index':32,'full_pass_fields':280,'pose_art':art,
            'unique_death_pose_records':len({row['native_pose'] for row in art}),
            'native_graphics_bank':{'source':'DFA78C','destination':'7F0000','bytes':len(bank),
                                    'compressed_bytes':compressed,'sha256':hashlib.sha256(bank).hexdigest(),
                                    'original_live_bank_matches':True},
            'native_checkpoint':checkpoint,'native_continue':continuing,'md_deaths':md_cases,
            'native_full_stream_field_checks':280*4,'md_live_stream_field_checks':225*8,
            'md_steering_axis_checks':201*8*2,'production_death_source_enabled':False,
            'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in (
                Path(__file__),out/'native/report.json',out/'native/samples.json',out/'native-continue/report.json',
                out/'native-continue/samples.json',out/'md/report.json',out/'md/samples.json',out/'md/callbacks.csv')},
            'remaining':['Native first-pose freeze and MD fade/main-loop ownership',
                         'Faithful selectable centering/display duration and final-life display skip',
                         'Audio-independent prelude/reload timing, original fallback, pause and save/yield contracts']}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original death33 poses/streams verified;1120 native and1800 MD live frame clocks,3216 steering axes;',
          'staging/final-life differences remain explicit; no production adapter enabled',flush=True)


if __name__=='__main__':main()
