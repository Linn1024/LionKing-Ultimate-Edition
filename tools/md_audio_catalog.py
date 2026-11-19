"""Render local MD soundtrack references through the ROM's original driver.

Run with .tools/python32/python.exe after scripts/BuildMDResearch.ps1.
These recordings are research artifacts and are never packaged with the game.
"""
from pathlib import Path
import argparse
import array
import json
import math
import struct
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds',type=float,default=5)
    args=ap.parse_args()
    if not 1<=args.seconds<=600: ap.error('--seconds must be between 1 and 600')
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    patterns=struct.unpack_from('>14H',rom,0x1d723c)
    dest=ROOT/'build/md-audio-catalog'; dest.mkdir(parents=True,exist_ok=True)
    results=[]; cache={}
    for level,pattern in enumerate(patterns):
        if pattern not in cache:
            game=MdLab()
            for _ in range(180): game.step()
            game.driver_step(1,pattern); game.samples.clear()
            for _ in range(round(args.seconds*game.av.timing.fps)): game.driver_step()
            values=array.array('h',game.samples)
            peak=max(map(abs,values),default=0)
            rms=math.sqrt(sum(x*x for x in values)/len(values)) if values else 0
            path=dest/f'pattern-{pattern:03x}.wav'
            with wave.open(str(path),'wb') as wav:
                wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(round(game.av.timing.sample_rate))
                wav.writeframes(game.samples)
            cache[pattern]={'pattern':pattern,'file':path.name,'peak':peak,'rms':round(rms,2)}
            game.close()
            if not peak: raise RuntimeError(f'pattern {pattern} rendered silent audio')
        results.append({'md_level':level+1,**cache[pattern]})
    report={'driver_dispatch': '0x2d0000', 'level_pattern_table':'0x1d723c','tracks':results}
    (dest/'catalog.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
