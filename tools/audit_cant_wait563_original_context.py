"""Resolve sound owners at exact original events instead of stale sparse actor slots."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
template=ROOT/'tools/md_replay_movie.py'
s=template.read_text()
s=s.replace("if index%100==0 or (transitions and transitions[-1]['frame']==index+1):", "if False:")
s=s.replace('game.step(pad);pointer=', 'game.step(pad);game.samples.clear();pointer=')
sys.argv=[str(template),'--movie',str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lag-reference',str(ROOT/'build/md-next-levels-reference/ram.csv'),'--frames','10330','--out',str(ROOT/'build/cant-wait563-original-context'),'--audio-events','--capture-at','5469','5487','7639','10284','10329','6000','7000']
exec(compile(s,str(template),'exec'))
