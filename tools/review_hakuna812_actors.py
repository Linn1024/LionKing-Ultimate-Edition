"""Color-correct local actor review sheets, using actual normal sprite palettes."""
import runpy,json,csv
from PIL import Image,ImageDraw
from audit_scenes import ROOT
d=runpy.run_path(str(ROOT/'tools/audit_hakuna792_actors.py'));ns=d['ns'];ms=d['ms'];image=d['image'];out=ROOT/'build/hakuna812-actors';out.mkdir(exist_ok=True)
families=[(5,'c58ee4','0e962e',0),(5,'c58e9c','0e96a4',3),(5,'c58ed8','0e962e',0),(5,'c58981','09792c',0),(5,'c58afc','0e9166',0),(5,'c58aec','0e914c',0),(5,'c58a97','0e96b2',1),(6,'c586d8','112330',0),(6,'c588dd','112564',2),(6,'c587e4','1125e4',2),(6,'c58844','112554',2),(6,'c586f0','111f00',2),(6,'c588b2','097836',0)]
for level,desc,mdesc,bank in families:
 nr=[r for r in ns if r['descriptor']==desc and ((int(r['frame'])<36500)==(level==5))];mr=[r for r in ms if r['descriptor']==mdesc and int(r['level'])==level]
 if not nr or not mr:continue
 np=list(dict.fromkeys(r['pose'] for r in nr))[:4];mp=list(dict.fromkeys(r['pose'] for r in mr))[:4]
 palette=[int(nr[0]['colors'][i:i+4],16) for i in range(0,64,4)]
 ncolors=[tuple(((c>>sh)&31)*255//31 for sh in (0,5,10)) for c in palette]
 m=d['m'];base=int.from_bytes(m[0x1cfdb4+level*48+44:0x1cfdb4+level*48+48],'big')+bank*32
 palette=[int.from_bytes(m[base+i*2:base+i*2+2],'big') for i in range(16)];mcolors=[tuple(((c>>sh)&7)*255//7 for sh in (1,5,9)) for c in palette]
 sheet=Image.new('RGB',(768,440),(32,32,32));draw=ImageDraw.Draw(sheet)
 for oy,rom,ps,md,colors in ((0,d['native'][level],np,False,ncolors),(220,d['external'][level],mp,True,mcolors)):
  for i,p in enumerate(ps):
   b=image(rom,p,md)
   if not b:continue
   x,y,w,h,pix=b;im=Image.new('RGB',(w,h));im.putdata([colors[c] if c else (32,32,32) for c in pix]);im=im.resize((w*2,h*2),Image.Resampling.NEAREST);sheet.paste(im,(i*192,oy+22));draw.text((i*192,oy),p,fill='white')
 sheet.save(out/f'{level}-{desc}.png')
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',families=families,scope=__doc__),indent=2)+'\n')
