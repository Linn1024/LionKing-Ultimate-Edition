"""Observe original lizard defeat handlers using ordinary first-level input."""
import argparse
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom


def md(out):
    import ctypes as C
    import array
    from md_lab import MdLab,png
    from md_replay_movie import movie_inputs
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    pads,_,settings=movie_inputs(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2')
    with (ROOT/'build/md-next-levels-reference/ram.csv').open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
    index=0;rows=[];previous={};previous_pose={};entries=[];last_image=None
    try:
        for frame in range(1,3001):
            trace.md_commands_frame(frame);game.step(polled[index])
            if trace.md_commands_polled():index+=1
            for actor in range(0x944e,0xa3ce,0x80):
                state=word(actor+0x30)<<16|word(actor+0x32)
                if state==0x19c554 and word(0xccce)==1:
                    if previous.get(actor)!=state:
                        entries.append({'frame':frame,'actor':actor,'from_state':previous.get(actor),'from_pose':previous_pose.get(actor)})
                        if last_image:png(out/f'before-{len(entries)}.png',*last_image)
                        png(out/f'entry-{len(entries)}.png',*game.image)
                    draw=word(actor+12)
                    rows.append({'frame':frame,'actor':actor,'timer':word(actor+0x2c),
                                 'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                                 'palette':word(draw+8)>>13&3,'x':word(actor+8),'y':word(actor+10),
                                 'palette_rgb9':list(struct.unpack_from('<16H',bytes(game.cram),(word(draw+8)>>13&3)*32)),
                                 'display_enabled':bool(game.reg[1]&64),'level_register':word(0xccce)})
                previous[actor]=state
                draw=word(actor+12)
                previous_pose[actor]=(word(draw+10)<<16|word(draw+12))&0xffffff
            last_image=game.image
    finally:trace.md_commands_close();game.close()
    calls=[r for r in csv.DictReader((out/'commands.csv').open())
           if r['selector']=='2' and r['value']=='165' and r['outer_caller']=='19c5c6']
    assert len(entries)==len(calls)==2 and rows
    metadata=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
    lizard_poses={int(r['md'],16) for r in metadata if r['role']=='lizard'}
    assert all(e['from_pose'] in lizard_poses for e in entries),'Defeated actor was not a reviewed lizard pose'
    lookup={(r['frame'],r['actor']):r for r in rows}
    assert all(lookup[(int(r['frame']),int(r['actor'],16))]['timer']==29 for r in calls)
    report={'result':'PASS','scope':__doc__,'source':'https://tasvideos.org/10612S',
            'original_handler':0x19c554,'script':0x9510a,'sound_return':0x19c5c6,
            'entries':entries,'calls':calls,'observations':rows,
            'timer_initial':32,'cue_before_decrement':30,'cue_after_decrement':29,
            'ordinary_input_no_guest_edits':True}
    report['zero_timer_rows_are_memory_observations_not_live_actor_proof']=True
    # Separately exercise the original driver, without game-action edits, to
    # ensure the existing120-field effect mix window retains the entire tail.
    probe=MdLab()
    try:
        for _ in range(180):probe.step()
        probe.samples.clear();peaks=[]
        for field in range(1,241):
            before=len(probe.samples);probe.driver_step(2 if field==1 else None,165)
            values=array.array('h',probe.samples[before:])
            peaks.append(max(map(abs,values),default=0))
    finally:probe.close()
    assert max(peaks)>500 and max(peaks[120:])==0
    report['controlled_original_driver_tail']={'fields':240,'peak':max(peaks),
        'last_field_peak_above_one':max(i+1 for i,p in enumerate(peaks) if p>1),
        'peak_after_field120':max(peaks[120:])}
    (out/'md.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MD: two original lizard defeat actions, FM165 at timer30 PASS',flush=True)


def native(out):
    read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--resource-profile',str(profile),'--lle','--frames','3000',
             '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape')]
    def run(name,frames):
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=','.join(map(str,frames)),TLK_WRAM_DIR=str(out),TLK_AUDIO_EVENTS=str(out/(name+'-events.csv')))
        with (out/(name+'.log')).open('wb') as f:subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
    def observations(frames):
        rows=[]
        for frame in frames:
            ram=(out/f'hl_wram_{frame}.bin').read_bytes();w=lambda a:struct.unpack_from('<H',ram,a)[0]
            if w(0x1ff9e) or w(0xdf) not in (0x387,0x80d):continue
            for actor in range(0xb293,0xc213,0x80):
                if w(actor+0x30)==0x6608 and w(actor+0x32)==0xc1:
                    draw=w(actor+12)
                    rows.append({'frame':frame,'actor':actor,'timer':w(actor+0x2c),
                                 'pose':int.from_bytes(ram[draw+10:draw+13],'little'),
                                 'palette':w(draw+8)>>1&7,'x':w(actor+8),'y':w(actor+10)})
        return rows
    coarse=list(range(1000,3001,8));run('coarse',coarse);found=observations(coarse)
    assert found,'No ordinary-input native defeat handler'
    fine=sorted({f for row in found for f in range(max(1,row['frame']-12),min(3000,row['frame']+13))})
    run('fine',fine);rows=observations(fine)
    entries=[r for i,r in enumerate(rows) if i==0 or r['frame']!=rows[i-1]['frame']+1 or r['actor']!=rows[i-1]['actor']]
    assert len(entries)>=2 and all(r['timer']==31 for r in entries)
    metadata=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
    lizard_poses={int(r['snes'],16) for r in metadata if r['role']=='lizard'}
    for entry in entries:
        ram=(out/f"hl_wram_{entry['frame']-1}.bin").read_bytes();actor=entry['actor']
        draw=struct.unpack_from('<H',ram,actor+12)[0]
        entry['from_pose']=int.from_bytes(ram[draw+10:draw+13],'little')
        entry['from_state']=int.from_bytes(ram[actor+0x30:actor+0x33],'little')
        assert entry['from_pose'] in lizard_poses,'Native defeated actor was not a reviewed lizard'
    assert all(not (int(e['actor'],16)==r['actor'] and int(e['frame'])==r['frame'])
               for e in csv.DictReader((out/'fine-events.csv').open()) for r in rows), 'Unexpected native cue in defeat action'
    report={'result':'PASS','scope':__doc__,'source':'Original native LLE, no MD ROM or source choices',
            'original_handler':0xc16608,'script':0xc25cae,'entries':entries,'observations':rows,
            'timer_initial':32,'no_original_sound_calls_in_observed_defeat_actions':True,
            'ordinary_input_no_guest_edits':True}
    report['zero_timer_rows_are_memory_observations_not_live_actor_proof']=True
    (out/'native.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Native:',len(entries),'ordinary lizard defeat actions, timer32 and no direct cue PASS',flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=('md','native'))
    args=ap.parse_args();out=ROOT/'build/lizard-defeat-original';out.mkdir(exist_ok=True)
    (md if args.mode=='md' else native)(out)


if __name__=='__main__':main()
