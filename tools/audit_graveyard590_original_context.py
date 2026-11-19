"""Capture exact original Graveyard cue owners once, retaining bounded RAM and selected pictures."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
template=ROOT/'tools/md_replay_movie.py';source=ROOT/'build/md-next-levels-replay'
levels={x['frame']:x['level'] for x in json.loads((source/'frames.json').read_text())}
fields=sorted({int(x['frame']) for x in csv.DictReader((source/'commands.csv').open()) if levels.get(int(x['frame']))==2 and int(x['selector']) in (2,19)})
s=template.read_text().replace("if index%100==0 or (transitions and transitions[-1]['frame']==index+1):",'if False:').replace('game.step(pad);pointer=','game.step(pad);game.samples.clear();pointer=')
s=s.replace("for name in ('work_ram','vram','cram','reg','vsram'):","for name in ('work_ram',):")
s=s.replace("if game.image:png(capture/'screen.png',*game.image)","if index+1 in (14000,16000,18000):png(capture/'screen.png',*game.image)")
sys.argv=[str(template),'--movie',str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lag-reference',str(ROOT/'build/md-next-levels-reference/ram.csv'),'--frames','18720','--out',str(ROOT/'build/graveyard590-original-context'),'--audio-events','--capture-at',*map(str,sorted(set(fields+[14000,16000,18000])))]
exec(compile(s,str(template),'exec'))
