"""Local sprite reference sheet; no generated art or data is shipped."""
import runpy
from PIL import Image,ImageDraw
from audit_scenes import ROOT
d=runpy.run_path(str(ROOT/'tools/audit_next731_sprites.py'));s=d['hydrated'][3];m=d['m'];image=d['image'];native=d['native'];external=d['external']
out=ROOT/'build/next734-art';out.mkdir(exist_ok=True)
for name,nd,md in [('cub','c5858a','07d728'),('wildebeest','c58b30','1b5b42'),('chameleon','c58ca4','09798e'),('running-lizard','c58c5c','097948'),('lizard','c58c50','09793a')]:
 level=4 if name in ('chameleon','running-lizard','lizard') else 3;s=d['hydrated'][level];m=d['md_hydrated'][level]
 ns=list(dict.fromkeys(r['pose'] for r in native if r['descriptor']==nd))[:16];ms=list(dict.fromkeys(r['pose'] for r in external if r['descriptor']==md and int(r['level'])==level))[:16]
 canvas=Image.new('RGB',(1024,600),(32,32,32));draw=ImageDraw.Draw(canvas)
 for row,rom,ps,ismd in [(0,s,ns,False),(1,m,ms,True)]:
  for i,p in enumerate(ps):
   b=image(rom,p,ismd)
   if not b:continue
   x,y,w,h,data=b;img=Image.new('RGB',(w,h));img.putdata([((c*17)%256,(c*47)%256,(c*97)%256) if c else (32,32,32) for c in data]);img=img.resize((w*2,h*2),Image.Resampling.NEAREST)
   ox=(i%8)*128;oy=row*300+(i//8)*150;canvas.paste(img,(ox,oy+20));draw.text((ox,oy),('MD ' if ismd else 'SNES ')+p,fill='white')
 canvas.save(out/(name+'.png'))
