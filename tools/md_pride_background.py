"""Original Pride Lands plane-B checks shared by reference replay diagnostics.

The original 64x45 panorama streams through a 64x32 VRAM ring. This recipe is
specific to Pride Lands; later scenes need independently established recipes.
"""
import struct
from md_assets import lz


class PrideBackgroundAudit:
    def __init__(self,rom):
        pointer=lambda offset:int.from_bytes(rom[0x1cfdb4+offset:0x1cfdb4+offset+4],'big')
        self.names=lz.decompress(rom,pointer(24))[0]
        self.tiles=lz.decompress(rom,pointer(28))[0]
        self.previous_camera=None

    def reset(self):
        self.previous_camera=None

    def sample(self,game):
        vram=bytes(game.vram);registers=bytes(game.reg);vsram=bytes(game.vsram)
        word=lambda data,at:struct.unpack_from('<H',data,at)[0]
        base=(registers[13]&63)<<10;table=(registers[4]&7)<<13
        bx=(-word(vram,base+2))&1023;by=word(vsram,2)&1023
        camera=[word(game.work_ram,0x880c),word(game.work_ram,0x880e)]
        errors=0;checked=0
        for ty in range(by//8,(by+223)//8+1):
            for tx in range(bx//8,(bx+319)//8+1):
                source=((ty%(len(self.names)//128))*64+(tx%64))*2
                actual=table+((ty%32)*64+(tx%64))*2
                errors+=int.from_bytes(self.names[source:source+2],'big')!=word(vram,actual)
                checked+=1
        packed=bytearray(len(self.tiles))
        packed[::2]=vram[1:len(self.tiles):2];packed[1::2]=vram[:len(self.tiles):2]
        prior=self.previous_camera
        self.previous_camera=camera
        return {'camera':camera,'scroll':[bx,by],
                'display_enabled':bool(registers[1]&0x40),
                'palette_nonzero':any(game.cram),
                'scroll_matches':None if prior is None else
                    bx==((prior[0]*38//256)&1023) and by==((prior[1]*20//256)&1023),
                'name_cells':checked,'name_errors':errors,'tiles_match':packed==self.tiles,
                'uniform_scroll':registers[11]==0 and registers[16]==1}
