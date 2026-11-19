"""Observe original MD scene initialization, line scroll and background assets.

Only levels 1/2 have hypotheses here; no game state is changed. A descriptor
pointer alone is insufficient during fades: normal palette/display are reported.
"""
import struct
from md_assets import lz


def palette_transition_step(current, target):
    """Original 18D7BA..18D818: one 3-bit step toward each target channel.

    The live controller trace checks every observed write against this recipe.
    Timing, target ownership and native correspondence remain separate.
    """
    result = 0
    for shift in (1, 5, 9):
        value = (current >> shift) & 7
        goal = (target >> shift) & 7
        value += (goal > value) - (goal < value)
        result |= value << shift
    return result


def line_offsets(level,camera_x):
    camera_x &= 65535
    if level==1:
        return [camera_x//4]*152+[camera_x//2]*40+[camera_x//2+((camera_x*(y-191))>>7) for y in range(192,224)]
    if level==2:
        return [camera_x//32]*96+[camera_x//16]*8+[camera_x//8]*24+[camera_x//4]*32+[camera_x//2]*64
    raise ValueError(level)


class SceneBackgroundAudit:
    def __init__(self,rom,levels):
        self.rom=rom;self.scenes={};self.previous={}
        for level in levels:
            ptr=lambda field:int.from_bytes(rom[0x1cfdb4+level*48+field:0x1cfdb4+level*48+field+4],'big')
            palette_sources=(0x1ea604,0x1ea684) if level==1 else (ptr(44),)
            palettes=[]
            for source in palette_sources:
                raw=struct.unpack_from('>64H',rom,source)
                palettes.append([(v>>1&7)|((v>>5&7)<<3)|((v>>9&7)<<6) for v in raw])
            self.scenes[level]=(lz.decompress(rom,ptr(24))[0],lz.decompress(rom,ptr(28))[0],palettes)
    def sample(self,game,level):
        names,tiles,palettes=self.scenes[level];vram=bytes(game.vram);regs=bytes(game.reg)
        word=lambda b,a:struct.unpack_from('<H',b,a)[0]
        camera=word(game.work_ram,0xcd36);x=word(game.work_ram,camera+8);extra=word(game.work_ram,0xcd00) if level==1 else 0
        input_x=(x+extra)&65535;prior=self.previous.get(level);self.previous[level]=input_x
        base=(regs[13]&63)<<10;table=(regs[4]&7)<<13;vertical=word(game.vsram,2)&1023
        scroll=[(-word(vram,(base+y*4+2)&65535))&1023 for y in range(224)]
        current=line_offsets(level,input_x);old=line_offsets(level,prior) if prior is not None else None
        current_errors=sum(a!=(b&1023) for a,b in zip(scroll,current));previous_errors=None if old is None else sum(a!=(b&1023) for a,b in zip(scroll,old))
        cells=set()
        for y,offset in enumerate(scroll):
            for tx in range(offset//8,(offset+319)//8+1):
                ty=(y+vertical)//8;cells.add(((ty%(len(names)//128))*64+(tx%64),(ty%32)*64+(tx%64)))
        errors=sum(int.from_bytes(names[a*2:a*2+2],'big')!=word(vram,(table+b*2)&65535) for a,b in cells)
        packed=bytearray(len(tiles));packed[::2]=vram[1:len(tiles):2];packed[1::2]=vram[:len(tiles):2]
        cram=list(struct.unpack('<64H',bytes(game.cram)))
        variants=[i for i,p in enumerate(palettes) if p[16:32]==cram[16:32]]
        return {'level':level,'camera_x':x,'offset_x':extra,'input_x':input_x,'display_enabled':bool(regs[1]&64),
                'palette_nonzero':any(cram),'normal_background_palette_variants':variants,'checkpoint_position':word(game.work_ram,0xccd6)<<16|word(game.work_ram,0xccd8),
                'line_scroll_mode':regs[11]&7,'size_mode':regs[16],'vertical':vertical,
                'scroll_current_errors':current_errors,'scroll_previous_errors':previous_errors,
                'name_cells':len(cells),'name_errors':errors,'base_tiles_match':packed==tiles,
                'scroll_bands':[[y,scroll[y]] for y in (0,95,96,103,104,127,128,151,152,159,160,191,192,223)]}
