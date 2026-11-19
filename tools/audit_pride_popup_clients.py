"""Check complete popup boundaries and independent HUD/position rendering."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels
from pride_sprite_catalog import bitmap,md_frame,snes_frame,pride_snes_graphics


def main():
    base=ROOT/'build/pride-popup-work';out=base/'client-audit';out.mkdir()
    path=base/'player-check4/report.json';report=json.loads(path.read_text())
    assert report['result']=='PASS'
    for name,sha in report['artifacts_sha256'].items():assert digest(path.parent/name)==sha
    md_path=ROOT/'Lion King, The (World).md';snes_path=ROOT/'Lion King, The (USA).sfc'
    md=md_path.read_bytes();snes=pride_snes_graphics(snes_path.read_bytes())
    checks={};changed_counts={}
    for row in report['observations']:
        side,width,field=row['label'].split('/');width=int(width)
        label=row['label'].replace('/','-');w,h,a=pixels(path.parent/f'{label}-native/window.png')
        _,_,b=pixels(path.parent/f'{label}-md/window.png')
        shift=width-256 if side=='right' else 0
        boxes=[((p['screen'][0]+shift)*3,p['screen'][1]*3,
                (p['screen'][0]+shift+p['size'])*3,(p['screen'][1]+p['size'])*3) for p in row['pieces']]
        bx,by,bw,bh,_=bitmap(md,md_frame(md,int(row['md_pose'],16)),True,with_origin=True)
        anchor=width-26 if side=='right' else 18
        boxes.append(((anchor+bx)*3,(20+by)*3,(anchor+bx+bw)*3,(20+by+bh)*3))
        changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
        checks[row['label']+'/only_popup_changed']=bool(changed) and all(
            any(x<=i%w<right and y<=i//w<bottom for x,y,right,bottom in boxes) for i in changed)
        changed_counts[row['label']]=len(changed)
    for side in ('right','left'):
        folder=path.parent/f'independent-{side}-native'
        scene=json.loads((folder/'scene.json').read_text())
        parts=[p for p in scene['pieces'] if p['popup_owner']]
        assert parts
        pose=parts[0]['pose'];x,y=parts[0]['actor_xy']
        bx,by,bw,bh,data=bitmap(snes,snes_frame(snes,pose&0x3fffff),False,with_origin=True)
        w,h,a=pixels(folder/'window.png')
        _,_,hud=pixels(path.parent/f'independent-{side}-hud/window.png')
        _,_,position=pixels(path.parent/f'independent-{side}-position/window.png')
        dx=4 if side=='right' else 2;dy=-4
        colors=scene['obj_palette0']
        native_unchanged=[];position_exact=[]
        for i,c in enumerate(data):
            if not c:continue
            px=x+bx+i%bw;py=y+by+i//bw
            at=(py*3+1)*w+px*3+1
            native_unchanged.append(a[at]==hud[at])
            expected=tuple(((colors[c]>>s&31)<<3)|((colors[c]>>s&31)>>2) for s in (0,5,10))
            moved=((py+dy)*3+1)*w+(px+dx)*3+1
            position_exact.append(position[moved]==expected)
        checks[side+'/hud_palette_does_not_recolour_popup']=bool(native_unchanged) and all(native_unchanged)
        checks[side+'/native_art_at_md_position']=bool(position_exact) and all(position_exact)
    paths=[Path(__file__),path,md_path,snes_path]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,changed_pixels=changed_counts,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'boundary/independence checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
