"""Inspect original MD streaming/palettes along a recorded first-level path.

This forcibly positions Simba from a local SNES RAM log. It is a graphics/loader
diagnostic, NEVER a gameplay-equivalence reference or legitimate playthrough.
Run with .tools/python32/python.exe after creating build/md-lab/game.state.
"""
import ctypes as C
import json
import struct
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png
from pride_sprite_catalog import read_rom
from md_pride_background import PrideBackgroundAudit

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audio-events',action='store_true')
    ap.add_argument('--out',type=Path,default=ROOT/'build/pride-md-path');args=ap.parse_args()
    game=MdLab();dest=args.out;dest.mkdir(parents=True,exist_ok=True)
    state=C.create_string_buffer((ROOT/'build/md-lab/game.state').read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(state)-1)
    trace=None
    if args.audio_events:
        trace=C.CDLL(str(ROOT/'build/md_trace.dll'))
        trace.md_trace_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.md_trace_init(game.core._handle,str(dest/'sound-events.csv').encode())
    rows=[line.split() for line in (ROOT/'build/allbugs-aot.ram').read_text().splitlines()]
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    background=PrideBackgroundAudit(rom)
    captures=[];last_palette=None;poses={};background_checks=[]
    for index,row in enumerate(rows[942:4162]):
        if trace:trace.md_trace_frame(index)
        x,y=int(row[4],16),int(row[5],16)
        for off,value in [(0x93d6,x),(0x93d8,y)]:
            game.work_ram[off]=value&255;game.work_ram[off+1]=value>>8
        pad=int(row[8],16);buttons=0
        # libretro A=Genesis C (jump), B=Genesis B (adult slash), Y=Genesis A (roar).
        for snes,md in [(0x100,7),(0x200,6),(0x400,5),(0x800,4),(0x8000,8),(0x80,1),(0x4000,0)]:
            if pad&snes:buttons|=1<<md
        game.step(buttons)
        def word(a):return game.work_ram[a&65535] | game.work_ram[(a+1)&65535]<<8
        at=word(0x90ca);seen=set()
        while at and at not in seen:
            seen.add(at);pose=(word(at+10)<<16|word(at+12))&0xffffff
            poses.setdefault(hex(pose),{'palette':(word(at+8)>>13)&3,'first_frame':index})
            at=word(at+2)
        background_checks.append({'frame':index,**background.sample(game)})
        palette=bytes(game.cram)
        if index%100==0 or palette!=last_palette:
            name=f'{index:04d}';png(dest/(name+'.png'),*game.image)
            (dest/(name+'-cram.bin')).write_bytes(palette)
            captures.append({'frame':index,'source_frame':int(row[0]),'x':x,'y':y,
                             'palette_changed':palette!=last_palette,
                             'palette':list(struct.unpack('<64H',palette))})
            if index in (0,2800,2900,3000):game.dump(dest/name)
        last_palette=palette
    game.dump(dest)
    (dest/'path.json').write_text(json.dumps({'scope':__doc__,'captures':captures,'poses':poses},indent=2)+'\n')
    (dest/'background-checks.json').write_text(json.dumps(background_checks,indent=2)+'\n')
    print('background checks:',len(background_checks),'frames,',sum(x['name_errors'] for x in background_checks),
          'name errors,',sum(x['scroll_matches'] is False for x in background_checks),'scroll errors,',
          sum(not x['tiles_match'] for x in background_checks),'tile errors')
    if trace:trace.md_trace_close()
    game.close();print('captured',len(captures),'path samples')

if __name__=='__main__':main()
