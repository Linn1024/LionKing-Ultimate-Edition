"""Replay an original MD movie from power-on without forcing game state.

Use .tools/python32/python.exe. A completed first level is reported separately
from full-movie/core synchronization; downloaded inputs remain in ignored build/.
"""
import argparse
import ctypes as C
import csv
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png
from pride_sprite_catalog import read_rom

def movie_inputs(path):
    with zipfile.ZipFile(path) as archive:
        header=archive.read('Header.txt').decode();settings=json.loads(archive.read('SyncSettings.json'))
        lines=archive.read('Input Log.txt').decode().splitlines()
    key=next(line for line in lines if line.startswith('LogKey:'))
    expected='P1 Up|P1 Down|P1 Left|P1 Right|P1 A|P1 B|P1 C|P1 Start|P1 X|P1 Y|P1 Z|P1 Mode'
    assert expected in key,'unsupported movie input layout'
    # libretro: Up, Down, Left, Right, Genesis A/B/C/Start/X/Y/Z/Mode.
    mapping=[4,5,6,7,1,0,8,3,10,9,11,2]
    pads=[]
    for line in lines:
        if not line.startswith('|'):continue
        fields=line.split('|');assert fields[1]=='..','movie resets need explicit replay support'
        assert len(fields[2])==12 and fields[3]=='.'*12,'unsupported player layout'
        pads.append(sum(1<<button for character,button in zip(fields[2],mapping) if character!='.'))
    return pads,header,settings

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--movie',type=Path,required=True)
    ap.add_argument('--frames',type=int,default=6000);ap.add_argument('--out',type=Path,default=ROOT/'build/md-tas/replay')
    ap.add_argument('--lag-reference',type=Path,help='Matching BizHawk RAM CSV; consume movie input per original controller read')
    ap.add_argument('--background-audit',action='store_true',help='Check original Pride Lands plane-B names, tiles and raster phase')
    ap.add_argument('--scene-audit',type=int,nargs='+',choices=(1,2),default=[])
    ap.add_argument('--capture-at',type=int,nargs='+',default=[])
    ap.add_argument('--audio-events',action='store_true');args=ap.parse_args()
    pads,header,settings=movie_inputs(args.movie)
    polled_pads=None
    if args.lag_reference:
        with args.lag_reference.open() as stream:
            polled_pads=[pads[int(row['frame'])-1] for row in csv.DictReader(stream)
                         if row['lag']=='0' and int(row['frame'])<=len(pads)]
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    digest=hashlib.md5(rom).hexdigest();assert digest.upper() in header.upper(),'movie ROM hash differs'
    args.out.mkdir(parents=True,exist_ok=True);game=MdLab();trace=None
    background=None;background_rows=[]
    scene_audit=None;scene_rows=[]
    if args.scene_audit:
        from md_scene_background import SceneBackgroundAudit
        scene_audit=SceneBackgroundAudit(rom,args.scene_audit)
    if args.background_audit:
        from md_pride_background import PrideBackgroundAudit
        background=PrideBackgroundAudit(rom)
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    six=settings['o']['UseSixButton'];device=513 if six else 257
    game.core.retro_set_controller_port_device(0,device);game.core.retro_set_controller_port_device(1,device)
    def word(a):a&=65535;return game.work_ram[a]|game.work_ram[(a+1)&65535]<<8
    def longword(a):return word(a)<<16|word(a+2)
    levels={struct.unpack_from('>I',rom,0x1cfdb4+i*48+4)[0]:i for i in range(14)}
    if args.audio_events or polled_pads is not None:
        trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.md_commands_init(game.core._handle,str(args.out/'commands.csv').encode())
    rows=[];transitions=[];previous=None;seen_pride=False;completed=False;poll_index=0
    try:
        for index,pad in enumerate(pads[:args.frames]):
            if polled_pads is not None:
                if poll_index>=len(polled_pads):raise RuntimeError('BizHawk input reference exhausted')
                pad=polled_pads[poll_index]
            if trace:trace.md_commands_frame(index+1)
            game.step(pad);pointer=longword(0xcd2e);level=levels.get(pointer)
            if polled_pads is not None and trace.md_commands_polled():poll_index+=1
            camera=word(0xcd36);player=word(camera+0x24) if 0x8000<=camera<=0xff80 else 0
            valid=0x8000<=player<=0xff80
            if pointer!=previous:
                transitions.append({'frame':index+1,'level':level,'collision_pointer':hex(pointer)})
                if level==0:seen_pride=True
                elif level==1 and seen_pride:completed=True
                previous=pointer
            row={'frame':index+1,'pad':pad,'poll':poll_index,'level':level,'collision_pointer':pointer,
                 # Collision records alias in bonuses and can remain stale in
                 # special stages. Keep the independent original level word.
                 'level_register':word(0xccce),
                 'reported_level':word(0xccce)-1 if 1<=word(0xccce)<=14 else None,
                 'rng':sum(game.work_ram[address^1]<<shift for address,shift in ((0x81ad,16),(0x81ae,8),(0x81af,0))),
                 'camera':[word(camera+8),word(camera+10)] if camera else None,
                 'player':[word(player+8),word(player+10)] if valid else None,
                 'health':word(0xccf6),'roar':word(0xccf2)}
            if valid and level==0:row['player_words']=[word(player+i*2) for i in range(64)]
            if background:
                if level==0 and valid and word(0xccf6)<=word(0xccf8):
                    background_rows.append({'frame':index+1,**background.sample(game)})
                else:background.reset()
            if scene_audit and level in args.scene_audit:
                scene_rows.append({'frame':index+1,**scene_audit.sample(game,level)})
            if index+1 in args.capture_at:
                capture=args.out/f'capture-{index+1}';capture.mkdir(exist_ok=True)
                for name in ('work_ram','vram','cram','reg','vsram'):
                    (capture/(name+'.bin')).write_bytes(bytes(getattr(game,name)))
                if game.image:png(capture/'screen.png',*game.image)
            rows.append(row)
            if index%100==0 or (transitions and transitions[-1]['frame']==index+1):
                (args.out/f'{index+1:05d}-wram.bin').write_bytes(bytes(game.work_ram))
                if game.image:png(args.out/f'{index+1:05d}.png',*game.image)
        if trace:trace.md_commands_close();trace=None
        game.dump(args.out/'final')
        report={'scope':__doc__,'movie':str(args.movie),'author':'ShgofcTAS','source':'https://tasvideos.org/10612S',
                'rom_md5':digest,'movie_header':header,'sync_settings':settings,'frames':len(rows),
                'first_level_completed':completed,'full_movie_synchronization_verified':False,
                'lag_reference':str(args.lag_reference) if args.lag_reference else None,'controller_polls':poll_index,
                'fps':game.av.timing.fps,'transitions':transitions,
                'wram_sha256':hashlib.sha256(bytes(game.work_ram)).hexdigest()}
        (args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        (args.out/'frames.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
        if scene_audit:
            (args.out/'scene-backgrounds.json').write_text(json.dumps(scene_rows,separators=(',',':'))+'\n')
        if background:
            (args.out/'background.json').write_text(json.dumps(background_rows,indent=2)+'\n')
            visible=[r for r in background_rows if r['display_enabled'] and r['palette_nonzero']]
            assert len(visible)>2000,'Insufficient live Pride Lands background coverage'
            assert all(r['name_errors']==0 and r['tiles_match'] and r['uniform_scroll'] for r in visible),'Original visible background stream differs'
            assert all(r['scroll_matches'] is not False for r in visible),'Original background raster phase differs'
            print('Unforced original Pride Lands background PASS:',len(visible),'visible frames;',len(background_rows)-len(visible),'blank transition frames',flush=True)
        print(json.dumps(report,indent=2),flush=True)
    finally:
        if trace:trace.md_commands_close()
        game.close()
    if not completed:raise SystemExit('Original MD first-level completion not established with this replay/core')

if __name__=='__main__':main()
