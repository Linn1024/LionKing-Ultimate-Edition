"""Audit first-level non-player art correspondence, including palette permutations."""
import csv
import json
from pride_sprite_catalog import ROOT,read_rom,pride_snes_graphics,snes_frame,md_frame,bitmap

def canonical(image):
    x,y,w,h,pixels=image
    colors={0:0};out=bytearray()
    for c in pixels:
        if c not in colors:colors[c]=len(colors)
        out.append(colors[c])
    return w,h,bytes(out)

def main():
    s=pride_snes_graphics(read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    candidates={};silhouettes={}
    for p in range(0,len(m)-40,2):
        if m[p] or m[p+1]>31:continue
        f=md_frame(m,p)
        if not f:continue
        image=bitmap(m,f,True,with_origin=True)
        if len(image)==5:
            candidates.setdefault(canonical(image),[]).append((p,image))
            key=(*image[2:4],bytes(bool(c) for c in image[4]))
            silhouettes.setdefault(key,[]).append((p,image))
    report=[]
    for row in csv.DictReader((ROOT/'build/pride-sprites/objects.csv').open()):
        if row['position']=='b21b':continue
        p=int(row['pose'],16);f=snes_frame(s,p&0x3fffff) if p>=0xc00000 else None
        item={'snes':hex(p),'palette':int(row['palette']),'position':row['position'],'matches':[],'silhouettes':[]}
        if f:
            image=bitmap(s,f,False,with_origin=True)
            if len(image)==5:
                for q,md_image in candidates.get(canonical(image),[]):
                    mapping={0:0}
                    for a,b in zip(image[4],md_image[4]):mapping[b]=a
                    item['matches'].append({'md':hex(q),'md_to_snes':mapping,'native_origin':image[:2],'md_origin':md_image[:2]})
                key=(*image[2:4],bytes(bool(c) for c in image[4]))
                for q,md_image in silhouettes.get(key,[]):
                    mapping={}
                    for a,b in zip(image[4],md_image[4]):mapping.setdefault(b,set()).add(a)
                    item['silhouettes'].append({'md':hex(q),'md_to_snes':{k:sorted(v) for k,v in mapping.items()},
                                                'native_origin':image[:2],'md_origin':md_image[:2]})
        report.append(item)
    path=ROOT/'build/pride-sprites/npc-catalog.json';path.write_text(json.dumps(report,indent=2)+'\n')
    mapped=sum(bool(x['matches']) for x in report)
    print(f'NPC pose/palette observations: {mapped}/{len(report)} exact art with bijective palette mapping')
    for palette in sorted({x['palette'] for x in report}):
        rows=[x for x in report if x['palette']==palette]
        print('palette',palette,'mapped',sum(bool(x['matches']) for x in rows),'silhouette',sum(bool(x['silhouettes']) for x in rows),'/',len(rows))

if __name__=='__main__':main()
