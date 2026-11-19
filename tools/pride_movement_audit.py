"""Controlled original-game movement samples, not a whole-behavior equivalence claim.

MD uses the pinned reference core and its local ready-state. SNES uses original
interpreter execution from the port's ready-state. Initial animation/lag phases
must be considered before treating observed differences as physics differences.
"""
import argparse
import ctypes as C
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom

CASES={'idle':0,'right':0x100,'left':0x200,'jump':0x8000,'right-jump':0x8100,
       'y-button':0x4000,'right-y-button':0x4100,'roar':0x80,'down-right':0x500,
       'down-y-button':0x4400,'down-right-y-button':0x4500,
       'walking-y-button':[0]*16+[0x100]*12+[0x4100]*12+[0]*24,
       'walking-down':[0]*16+[0x100]*12+[0x500]*12+[0]*24,
       'short-jump':[0]*16+[0x8000]*4+[0]*44,
       'air-reverse':[0]*16+[0x8100]*10+[0x8200]*10+[0]*28,
       'jump-roar':[0]*16+[0x8000]*8+[0x80]*8+[0]*32}
def pads(buttons):return buttons if isinstance(buttons,list) else [0]*16+[buttons]*20+[0]*28

# Ordinary-input action variants; separate from the historical movement set.
ROAR_VARIANTS={
    'roar':[0]*16+[0x80]*20+[0]*92,
    'held-roar':[0]*16+[0x80]*220+[0]*64,
    'repeat-roar':[0]*16+[0x80]*20+[0]*40+[0x80]*20+[0]*120,
    'jump-roar':[0]*16+[0x8000]*8+[0x80]*20+[0]*128,
}

# Input-only rolling protocols, including both directions and interruptions.
# A longer right walk gives the left-roll cases room before the left boundary.
ROLL_VARIANTS={
    'standing-down':[0]*16+[0x400]*24+[0]*96,
    'low-speed-roll':[0]*16+[0x100]+[0x500]*12+[0]*96,
    'right-roll-release':[0]*16+[0x100]*12+[0x500]*12+[0]*96,
    'right-roll-held':[0]*16+[0x100]*12+[0x500]*80+[0]*64,
    'left-roll-release':[0]*16+[0x100]*52+[0x200]*12+[0x600]*12+[0]*96,
    'left-roll-held':[0]*16+[0x100]*52+[0x200]*12+[0x600]*64+[0]*96,
    'roll-reverse':[0]*16+[0x100]*12+[0x500]*6+[0x600]*6+[0]*128,
    'roll-held-reverse':[0]*16+[0x100]*12+[0x500]*8+[0x600]*64+[0]*96,
    'jump-during-roll':[0]*16+[0x100]*12+[0x500]*6+[0x8100]*4+[0x100]*20+[0]*96,
    'roar-during-roll':[0]*16+[0x100]*12+[0x500]*6+[0x180]*20+[0]*128,
    'down-without-direction':[0]*16+[0x100]*12+[0x500]*12+[0x400]*20+[0]*96,
    'repeated-roll':[0]*16+[0x100]*12+[0x500]*12+[0x100]*50+[0x500]*12+[0]*128,
    'airborne-down':[0]*16+[0x8100]*8+[0x500]*24+[0]*128,
    'left-boundary-roll':[0]*16+[0x200]*8+[0x600]*8+[0]*128,
    'paused-roll':[0]*16+[0x100]*12+[0x500]*4+[0x1000]+[0]*12+[0x1000]+[0]*96,
}

# Longer input-only paths deliberately reach more enemies and uneven terrain.
# These are research fixtures, not an asserted equivalence set.
ROLL_CONTACT_VARIANTS={
    'long-roll-chase':[0]*16+[0x100]*12+[0x500]*240+[0]*96,
    'repeated-roll-chase':[0]*16+[0x100]*12+[0x500]*12+[0x100]*50+[0x500]*12+
                          [0x100]*100+[0x500]*12+[0x100]*100+[0]*96,
    'chase-and-return':[0]*16+[0x100]*12+[0x500]*80+[0x100]*80+
                        [0x200]*120+[0x600]*60+[0]*96,
}

def raw_slots(word,source):
    """Raw allocated-slot observations; retained state is not active-list proof."""
    first,last=(0xb293,0xc213) if source=='snes' else (0x944e,0xa3ce)
    rows=[]
    for actor in range(first,last,0x80):
        words=[word(actor+i*2) for i in range(64)]
        state=words[24]|words[25]<<16 if source=='snes' else words[24]<<16|words[25]
        if state:
            item={'actor':actor,'state':state,'words':words}
            draw=words[6]
            if 0x8000<=draw<=0xffe8:
                item['draw_pose']=((word(draw+10)|word(draw+12)<<16)&0x3fffff if source=='snes'
                                   else (word(draw+10)<<16|word(draw+12))&0xffffff)
                item['draw_attributes']=word(draw+8)
            rows.append(item)
    return rows
def snes(ready,settle=0,tail=0,md_start=False,md_camera=False,actor_slots=False,ordinary_boot=False,md_activation=False,md_reactivation=False,md_body_bounds=''):
    read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    ready.mkdir(parents=True,exist_ok=True)
    profile=ready/'native.ini';profile.write_text('schema = 1\ngame = snes\n'+
        ('gameplay.levels.pride_lands.start = md\n' if md_start else '')+
        ('gameplay.camera = md\ndisplay.viewport = md\n' if md_camera else '')+
        ('gameplay.levels.pride_lands.activation = md\n' if md_activation else '')+
        ('gameplay.levels.pride_lands.lizard_reactivation = md\n' if md_reactivation else '')+
        ('gameplay.hitboxes.simba = md\n' if md_body_bounds in ('simba','both') else '')+
        ('gameplay.hitboxes.enemies = md\n' if md_body_bounds in ('enemies','both') else ''))
    config=ready/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    state=ready/'ready-native.state'
    cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
         '--resource-profile',str(profile),'--config',str(config),
         '--lle','--frames','2200','--save-at','2200',str(state),'--no-pace','--no-audio','--no-record']
    if ordinary_boot:
        raw=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()
        words=struct.unpack('<'+'H'*(len(raw)//2),raw)
        prefix=ready/'ordinary-boot.polled.tape';prefix.write_bytes(raw[:words.index(0x100)*2])
        cmd+=['--input-polled',str(prefix)]
    else:cmd+=['--practice-level','0']
    if md_start or md_camera or md_activation or md_reactivation or md_body_bounds:cmd+=['--md-rom',str(ROOT/'Lion King, The (World).md')]
    with (ready/'prepare-native.log').open('wb') as log:
        subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    header=state.read_bytes()[:16]
    assert header[:8]==b'TLKSTAT1';start=struct.unpack_from('<I',header,12)[0]+settle
    results={}
    for case,buttons in CASES.items():
        folder=ready/case/'snes';folder.mkdir(parents=True,exist_ok=True)
        actions=pads(buttons)+[0]*tail;tape=folder/'input.tape'
        tape.write_bytes(struct.pack('<'+'H'*(start+len(actions)),*([0]*start+actions)))
        env=os.environ.copy();env['TLK_WRAM_DUMP']=','.join(str(start+n+1) for n in range(len(actions)));env['TLK_WRAM_DIR']=str(folder)
        command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--lle','--load',str(state),'--frames',str(start+len(actions)),'--input',str(tape)]
        if md_start or md_camera or md_activation or md_reactivation or md_body_bounds:command+=['--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile)]
        with (folder/'game.log').open('wb') as output:
            subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=90)
        rows=[]
        for n,pad in enumerate(actions):
            ram=(folder/f'hl_wram_{start+n+1}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
            assert word(0x1ff9e)==0 and word(0xdf) in (0x387,0x80d),'not Pride Lands'
            draw=word(0xb21f);assert draw+22<=65536,'Invalid cub draw record'
            rows.append({'frame':n,'pad':pad,'x':word(0xb21b),'y':word(0xb21d),'health':word(0x2004),
                         'roar':word(0x2002),'roar_active':word(0xa698),'words':list(struct.unpack_from('<64H',ram,0xb213)),
                         'pose':int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff,
                         'draw_words':list(struct.unpack_from('<11H',ram,draw))})
            if actor_slots:
                rows[-1]['raw_slots']=raw_slots(word,'snes')
                rows[-1]['camera_words']=[word(0xb293+i*2) for i in range(64)]
                rows[-1]['spawn_bounds']=[word(at) for at in (0xb1ff,0xb201,0xb203,0xb205)]
        results[case]=rows
    return results

def md(settle=0,tail=0,fresh_ready=None,actor_slots=False):
    from md_lab import MdLab,png
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab()
    if fresh_ready is not None:
        # Reproduce md_lab's ordinary Start-button boot, without borrowing an
        # old core checkpoint or editing actor/camera/game clock state.
        for n in range(1800):game.step((1<<3) if 200<n<1500 and n%90<3 else 0)
        game.core.retro_serialize_size.restype=C.c_size_t
        size=game.core.retro_serialize_size();snapshot=C.create_string_buffer(size)
        game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
        game.core.retro_serialize.restype=C.c_bool
        assert game.core.retro_serialize(snapshot,size)
        raw=snapshot.raw
        assert b'TLKAE001' in raw,'Fresh reference checkpoint must retain complete core timing/audio history'
        (fresh_ready/'ready-md.state').write_bytes(raw)
    else:raw=(ROOT/'build/md-lab/game.state').read_bytes()
    state=C.create_string_buffer(raw)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    results={}
    try:
        for case,buttons in CASES.items():
            assert game.core.retro_unserialize(state,len(state)-1)
            for _ in range(settle):game.step()
            player=word(word(0xcd36)+0x24);assert player==0x93ce
            rows=[]
            for n,pad in enumerate(pads(buttons)+[0]*tail):
                mapped=0
                # libretro A=Genesis C (jump), B=Genesis B (adult slash), Y=Genesis A (roar).
                for native,button in [(0x100,7),(0x200,6),(0x400,5),(0x800,4),(0x8000,8),(0x80,1),(0x4000,0),(0x1000,3)]:
                    if pad&native:mapped|=1<<button
                game.step(mapped)
                draw=word(player+12);assert draw+22<=65536,'Invalid cub draw record'
                rows.append({'frame':n,'pad':pad,'x':word(player+8),'y':word(player+10),
                             'health':word(0xccf6),'roar':word(0xccf2),'roar_active':word(0xccf4),
                             'words':[word(player+i*2) for i in range(64)],
                             'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                             'draw_words':[word(draw+i*2) for i in range(11)]})
                if actor_slots:
                    rows[-1]['raw_slots']=raw_slots(word,'md')
                    camera=word(0xcd36);assert 0x8000<=camera<=0xff80
                    rows[-1]['camera_words']=[word(camera+i*2) for i in range(64)]
                    rows[-1]['spawn_bounds']=[word(at) for at in (0xe930,0xe932,0xe934,0xe936)]
                    if fresh_ready and n in (0,40,43,118,119,133,219,220,221,222):
                        folder=fresh_ready/case;folder.mkdir(exist_ok=True)
                        (folder/f'md-wram-{n}.bin').write_bytes(bytes(game.work_ram))
                        png(folder/f'md-{n}.png',*game.image)
            results[case]=rows
    finally:game.close()
    return results

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',choices=['snes','md'],required=True)
    ap.add_argument('--out',type=Path,default=ROOT/'build/pride-movement');ap.add_argument('--settle-frames',type=int,default=0);ap.add_argument('--tail-frames',type=int,default=0)
    variants=ap.add_mutually_exclusive_group()
    variants.add_argument('--roar-variants',action='store_true',help='Use held, repeated and airborne roar protocols instead of the movement set')
    variants.add_argument('--roll-variants',action='store_true',help='Use rolling direction/entry/hold/interrupt/boundary protocols')
    variants.add_argument('--roll-contact-variants',action='store_true',help='Research longer rolling paths into enemies and uneven terrain')
    ap.add_argument('--fresh-md-ready',action='store_true',help='Boot the MD ready checkpoint again using ordinary Start inputs')
    ap.add_argument('--md-start',action='store_true',help='Select only the MD initial-position layout in the native host')
    ap.add_argument('--md-camera',action='store_true',help='Select MD camera/320 viewport and its original wider spawn window in the native host')
    ap.add_argument('--actor-slots',action='store_true',help='Include raw actor slots; retained state is not proof of active membership')
    ap.add_argument('--ordinary-boot',action='store_true',help='Use the ordinary native controller boot prefix, then neutral input, instead of the practice menu')
    ap.add_argument('--md-activation',action='store_true',help='Select MD initial enemy activation order in the native host')
    ap.add_argument('--md-reactivation',action='store_true',help='Select MD lizard offscreen reactivation position in the native host')
    ap.add_argument('--md-body-bounds',choices=('simba','enemies','both'),default='',help='Select independently ROM-backed actor body bounds')
    args=ap.parse_args()
    if args.roar_variants:CASES.clear();CASES.update(ROAR_VARIANTS)
    if args.roll_variants:CASES.clear();CASES.update(ROLL_VARIANTS)
    if args.roll_contact_variants:CASES.clear();CASES.update(ROLL_CONTACT_VARIANTS)
    if args.fresh_md_ready and args.source!='md':ap.error('--fresh-md-ready requires --source md')
    if args.md_start and args.source!='snes':ap.error('--md-start requires --source snes')
    if args.md_camera and args.source!='snes':ap.error('--md-camera requires --source snes')
    if args.ordinary_boot and args.source!='snes':ap.error('--ordinary-boot requires --source snes')
    if args.md_activation and args.source!='snes':ap.error('--md-activation requires --source snes')
    if args.md_reactivation and args.source!='snes':ap.error('--md-reactivation requires --source snes')
    if args.md_body_bounds and args.source!='snes':ap.error('--md-body-bounds requires --source snes')
    assert 0<=args.settle_frames<=3600 and 0<=args.tail_frames<=512
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    data=snes(out,args.settle_frames,args.tail_frames,args.md_start,args.md_camera,args.actor_slots,args.ordinary_boot,args.md_activation,args.md_reactivation,args.md_body_bounds) if args.source=='snes' else md(args.settle_frames,args.tail_frames,out if args.fresh_md_ready else None,args.actor_slots)
    checkpoint=out/'ready-native.state' if args.source=='snes' else out/'ready-md.state' if args.fresh_md_ready else ROOT/'build/md-lab/game.state'
    (out/(args.source+'.json')).write_text(json.dumps({'scope':__doc__,'settle_frames':args.settle_frames,'tail_frames':args.tail_frames,
        'fresh_md_input_boot':args.fresh_md_ready,'md_start_selected':args.md_start,
        'md_camera_selected':args.md_camera,
        'raw_slots_may_be_inactive':args.actor_slots,
        'ordinary_native_input_boot':args.ordinary_boot,
        'md_activation_selected':args.md_activation,
        'md_reactivation_selected':args.md_reactivation,
        'md_body_bounds_selected':args.md_body_bounds,
        'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest() if args.source=='snes' else None,
        'headless_sha256':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest() if args.source=='snes' else None,
        'ready_checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'cases':data},indent=2)+'\n')
    for case,rows in data.items():print(args.source,case,'start',rows[15]['x'],rows[15]['y'],'held end',rows[35]['x'],rows[35]['y'],flush=True)

if __name__=='__main__':main()
