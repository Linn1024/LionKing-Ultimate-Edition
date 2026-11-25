"""Compare tile runs with scalar sampling using synthetic, ROM-free scenes."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class MdTileRuns(unittest.TestCase):
    def test_scalar_equivalence(self):
        compiler = shutil.which("gcc") or shutil.which("cc")
        if not compiler:
            self.skipTest("C compiler unavailable")
        source = Path(__file__).resolve().parents[2] / "runner/tlk_md_assets.c"
        harness = '#include "md_assets.c"\n' + r'''
#include <assert.h>
static uint8_t tiles[28448+4*1440], map[2], blocks[16], background[8192], native_map[2];
static uint16_t native_blocks[1], paired[1];
static void put(uint8_t *p,unsigned value){p[0]=value>>8;p[1]=value;}
static void setup(unsigned level,unsigned flags,int phase){
 MdScene *s=&scenes[level];memset(s,0,sizeof *s);s->valid=1;
 s->tiles=tiles;s->tile_size=sizeof tiles;s->map=map;s->map_size=2;
 s->row_bytes=2;s->rows=1;s->blocks=blocks;s->block_size=sizeof blocks;
 s->background=background;s->bg_size=sizeof background;
 s->native_blocks=native_blocks;s->native_count=1;
 s->native_map=native_map;s->native_map_size=2;s->native_row_bytes=2;s->paired_blocks=paired;
 native_blocks[0]=0;paired[0]=8;memset(native_map,0,sizeof native_map);memset(map,0,sizeof map);
 for(unsigned i=0;i<8;i++)put(blocks+2*i,flags+(level==5?889:i));
 for(unsigned i=0;i<sizeof background;i+=2)put(background+i,flags+(level==5?889:(i/2)%8));
 TlkMdSceneAnimationPhase(5,(unsigned)phase);
}
static void check(unsigned level,unsigned cell,unsigned x,unsigned y,unsigned count){
 uint16_t out[10];for(unsigned i=0;i<10;i++)out[i]=0xbeef;
 assert(TlkMdSceneMappedPixels(level,cell,x,y,out+1,count));
 for(unsigned i=0;i<count;i++)assert(out[i+1]==TlkMdSceneMappedPixel(level,cell,x+i,y));
 assert(out[0]==0xbeef && out[count+1]==0xbeef);
 assert(TlkMdSceneForegroundPixels(level,(int)x,(int)y,out+1,count));
 for(unsigned i=0;i<count;i++)assert(out[i+1]==TlkMdScenePixel(level,0,x+i,y,0,0,0,0,0,0,0,512));
 assert(out[0]==0xbeef && out[count+1]==0xbeef);
 assert(TlkMdSceneBackgroundPixels(level,(int)x,(int)y,out+1,count));
 for(unsigned i=0;i<count;i++)assert(out[i+1]==TlkMdScenePixel(level,1,0,0,0,0,x+i,y,0,0,0,512));
 assert(out[0]==0xbeef && out[count+1]==0xbeef);
}
int main(void){
 for(unsigned i=0;i<sizeof tiles;i++)tiles[i]=(i%11)?(uint8_t)((i/32)*3+(i%32)*7):0;
 for(unsigned pass=0;pass<5;pass++)for(unsigned bits=0;bits<32;bits++){
  unsigned level=pass?5:0;
  unsigned flags=((bits&1)?0x8000:0)|((bits>>1&3)<<13)|((bits&8)?0x800:0)|((bits&16)?0x1000:0);
  setup(level,flags,pass?pass-1:0);
  for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++)for(unsigned n=1;n<=8-(x&7);n++){
   check(level,0,x,y,n); /* Exact native map match selects the paired MD block. */
   check(level,7,x,y,n); /* Low cell flags differ: use the generic correspondence. */
  }
 }
 uint16_t out[8];for(unsigned i=0;i<8;i++)out[i]=0xbeef;
 assert(!TlkMdSceneMappedPixels(0,8,0,0,out,8));
 assert(!TlkMdSceneMappedPixels(0,0,0,0,out,0));
 assert(!TlkMdSceneMappedPixels(0,0,7,0,out,2));
 assert(!TlkMdSceneForegroundPixels(0,-1,0,out,1));
 assert(!TlkMdSceneForegroundPixels(0,16,0,out,1));
 assert(!TlkMdSceneBackgroundPixels(0,7,0,out,2));
 assert(!TlkMdSceneBackgroundPixels(14,0,0,out,1));
 for(unsigned i=0;i<8;i++)assert(out[i]==0xbeef);
 assert(TlkMdSceneBackgroundPixels(0,-1,-1,out,1));
 assert(out[0]==TlkMdScenePixel(0,1,0,0,0,0,-1,-1,0,0,0,512));
}
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            # Cache file IO needs framework SHA support, but is unrelated to
            # decoded pixel sampling. Keep this harness independent of ROMs
            # and framework checkouts; the tested functions are unmodified.
            (path / "md_assets.c").write_text(source.read_text().replace(
                '#include "tlk_md_assets_cache.inc"', ''))
            (path / "test.c").write_text(harness)
            binary = path / "test.exe"
            result = subprocess.run([compiler, "-std=c11", "-O2", "-ffunction-sections",
                                     "-fdata-sections", "-I", str(source.parent),
                                     str(path / "test.c"),
                                     "-Wl,--gc-sections", "-o", str(binary)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
