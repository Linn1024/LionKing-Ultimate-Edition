"""One current moving-platform field verifies scoped colors and native/gameplay preservation."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait441_monkeys.py')
s=template.read_text()
# Use the settled fixture test's compact native/selected checks, without a level prefix.
a=s.index("reference=ROOT/");b=s.index('env={k:v',a)
s=s[:a]+'''reference=ROOT/'build/graveyard522-enemies/report.json';ref=bound(reference)
build=ROOT/'build/graveyard536/build-report.json';bound(build)
out=ROOT/'build/graveyard537-bones';out.mkdir(exist_ok=True)
base=ref['command'].copy();i=base.index('--save-at');del base[i:i+3];i=base.index('--input-polled');del base[i:i+2]
base[base.index('--load')+1]=str(reference.parent/'enemies.state')
base[base.index('--frames')+1]='14251';base[base.index('--hash-at')+1]='14251';base[base.index('--sprite-assets')+1]=str(ROOT/'build/graveyard529-helper/sprites.assets')
''' +s[b:]
s=s.replace("ROOT/'dist/installed-preview418/LionKing.exe'", "ROOT/'build/graveyard530/player.exe'")
s=s.replace('graphics.sprites.animals.monkeys.palette','graphics.sprites.bones.palette')
s=s.replace("'schema = 1\\ngame = snes\\ndisplay.viewport = md\\ngraphics.scenery = md\\n'", "'schema = 1\\ngame = snes\\ndisplay.viewport = md\\n'")
s=s.replace('0xc58be4','0xc58e1c')
s=s.replace("ROOT/'build/cant-wait437-monkeys/report.json'", "ROOT/'build/graveyard534-bones/report.json'")
s=s.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template,reference,')
# Replace inherited monkey mask with the four actually bound platform actors.
a=s.index('for p in scene[\'pieces\']:');b=s.index('outside=',a)
s=s[:a]+'''for p in scene['pieces']:
    if p['palette']!=7 or p['actor_descriptor'] not in (0xc58e1c,0xc58e36,0xc58e50,0xc58e6a):continue
    x,y=p['screen'];n=p['size'];draw.rectangle(((x+column)*scale,y*scale,(x+column+n)*scale-1,(y+n)*scale-1),fill=255);monkeys+=1
''' +s[b:]
s=s.replace('monkeys','platforms').replace('monkey','platform')
exec(compile(s,str(template),'exec'))
