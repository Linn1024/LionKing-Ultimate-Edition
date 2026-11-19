"""Re-emit four reviewed semantic rows without rewriting frozen discovery data."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_sprite_catalog import read_rom,pride_snes_graphics,snes_frame,md_frame,bitmap


def main():
    out=ROOT/'build/pride-continue-token-map';out.mkdir()
    header=ROOT/'engine/generated/resources/pride_sprite_map.h'
    previous=ROOT/'build/pride-continue-token-origin-baseline/engine/generated/resources/pride_sprite_map.h'
    assert header.read_bytes()==previous.read_bytes()
    s=pride_snes_graphics(read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'))
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    metadata=ROOT/'tools/pride_npc_pairs.json';pairs=[r for r in json.loads(metadata.read_text())['pairs'] if r['role']=='continue_token'];assert len(pairs)==4
    text=header.read_bytes();changes=[]
    for row in pairs:
        p=int(row['snes'],16)&0x3fffff;q=int(row['md'],16)
        a=bitmap(s,snes_frame(s,p),False,with_origin=True);b=bitmap(m,md_frame(m,q),True,with_origin=True)
        assert a[0]==b[0] and a[1]==b[1]+1 and a[2:]==b[2:] and row['native_palette']==row['md_palette']==0
        x,y,w,h,_=b;prefix=('{0x%x,'%p).encode();lines=text.splitlines(keepends=True);indices=[i for i,line in enumerate(lines) if line.startswith(prefix)];assert len(indices)==1
        i=indices[0];old=lines[i];ending=b'\r\n' if old.endswith(b'\r\n') else b'\n'
        identity=','.join(map(str,range(16)))
        new=('{0x%x, 0x%x, %d, %d, %d, %d, 0, {{0,0,0}},8,0,0, {%s}, {%s}},'%(p,q,x,y,w,h,identity,identity)).encode()+ending
        lines[i]=new;text=b''.join(lines);changes.append(dict(native=p,md=q,native_origin=a[:2],md_origin=b[:2],size=b[2:4],old_row=old.decode().strip(),new_row=new.decode().strip()))
    old_lines=previous.read_bytes().splitlines();new_lines=text.splitlines();assert len(old_lines)==len(new_lines) and sum(a!=b for a,b in zip(old_lines,new_lines))==4
    header.write_bytes(text)
    paths=[Path(__file__),header,previous,metadata,ROOT/'tools/pride_sprite_catalog.py']
    report=dict(result='PASS',checks=dict(only_four_rows_changed=True,all_four_indexed_images_identical=True,original_md_y_is_native_minus_one=True),
                changes=changes,frozen_discovery_catalog_not_overwritten=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS four semantic rows; other899 rows retained',flush=True)


if __name__=='__main__':main()
