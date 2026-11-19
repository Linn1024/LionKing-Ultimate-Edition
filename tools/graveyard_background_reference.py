"""Export original Elephant Graveyard plane-B tokens, without host rendering.

Requires the unforced MD replay's raw VDP captures and per-frame scene audit.
Generated cartridge-derived pixels remain under ignored build/.
"""
import argparse,json,struct
from pathlib import Path
from audit_scenes import ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--replay',type=Path,default=ROOT/'build/md-next-levels-replay');args=ap.parse_args()
    rows=json.loads((args.replay/'scene-backgrounds.json').read_text());by_frame={r['frame']:r for r in rows}
    out=ROOT/'build/graveyard-background';out.mkdir(parents=True,exist_ok=True)
    frames=(14000,16000,18000);report=[]
    with (out/'original-pixels.bin').open('wb') as f:
        f.write(b'GRAVBG01'+struct.pack('<I',len(frames)))
        for frame in frames:
            row=by_frame[frame];prior=by_frame[frame-1];assert row['level']==2 and row['scroll_previous_errors']==0 and row['normal_background_palette_variants']
            d=args.replay/f'capture-{frame}';vram=(d/'vram.bin').read_bytes();reg=(d/'reg.bin').read_bytes();vs=(d/'vsram.bin').read_bytes()
            word=lambda b,a:struct.unpack_from('<H',b,a)[0]
            assert reg[11]==3 and reg[16]==1 and word(vs,2)==0
            table=(reg[4]&7)<<13;hbase=(reg[13]&63)<<10;tokens=[]
            for y in range(224):
                scroll=(-word(vram,hbase+4*y+2))&1023
                for x in range(320):
                    wx=(x+scroll)&511;tile=word(vram,table+(y//8*64+wx//8)*2);xx=wx&7;yy=y&7
                    if tile&0x800:xx=7-xx
                    if tile&0x1000:yy=7-yy
                    packed=vram[((tile&2047)*32+yy*4+xx//2)^1];pixel=(packed>>(0 if xx&1 else 4))&15
                    tokens.append(((11 if tile&0x8000 else 7)<<12)|0x900|((tile>>13)&3)*16|pixel if pixel else 0)
            f.write(struct.pack('<iIII',prior['input_x'],320,224,0));f.write(struct.pack('<'+'H'*len(tokens),*tokens))
            report.append({'frame':frame,'view_left':prior['input_x'],'pixels':len(tokens)})
    (out/'original-pixels.json').write_text(json.dumps({'scope':__doc__,'samples':report},indent=2)+'\n')
    print('Original Elephant Graveyard background pixels exported:',sum(r['pixels'] for r in report),flush=True)


if __name__=='__main__':main()
