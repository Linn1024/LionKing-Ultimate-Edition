"""Explain the return-path contact gap using original pose headers and live RAM.

Computes the original inclusive rectangle comparisons on actual pre-contact
snapshots. This is source/data evidence, not a whole-game completion claim.
"""
import hashlib
import json
import struct
from audit_scenes import ROOT, read_rom


def bounds(rom,pose,x,y,attributes,md):
    left,top,right,bottom=struct.unpack_from('>4h' if md else '<4h',rom,pose+12)
    if attributes&(0x800 if md else 0x40):left,right=-right,-left
    if attributes&(0x1000 if md else 0x80):top,bottom=-bottom,-top
    return [x+left,y+top,x+right,y+bottom]


def overlap(a,b):
    return a[2]>=b[0] and a[3]>=b[1] and a[0]<=b[2] and a[1]<=b[3]


def main():
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    source=ROOT/'build/pride-activation-reactivation-contacts/chase-and-return/snes/hl_wram_2677.bin'
    ram=source.read_bytes();w=lambda p:struct.unpack_from('<H',ram,p)[0]
    player=0xb213;enemy=0xb413;draw=w(enemy+12)
    native_pose=int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff
    native_box=bounds(snes,native_pose,w(enemy+8),w(enemy+10),w(draw+8),False)
    native_player=list(struct.unpack_from('<4h',ram,0xf942))
    original_path=ROOT/'build/pride-roll-contact-boxes/md.json'
    rows=json.loads(original_path.read_text())['cases']['chase-and-return']
    row=rows[220];actors=[a for a in row['raw_slots'] if a['actor']==0x984e]
    assert len(actors)==1;actor=actors[0]
    external_box=bounds(md,actor['draw_pose'],actor['words'][4],actor['words'][5],actor['draw_attributes'],True)
    external_player=bounds(md,row['pose'],row['x'],row['y'],row['draw_words'][4],True)
    assert native_pose==0x2f0e6 and actor['draw_pose']==0xb8204
    assert [w(enemy+8),w(enemy+10)]==actor['words'][4:6]==[473,1261]
    assert [w(player+8),w(player+10)]==[row['x'],row['y']]==[502,1261]
    assert not overlap(native_box,native_player) and overlap(external_box,external_player)
    assert native_box[2]==483 and external_box[2]==485 and native_player[0]==external_player[0]==485
    assert md[0x18d624]==md[0x18d628]==0x6d and md[0x18d62c]==md[0x18d630]==0x6e
    assert snes[0xd56c:0xd56f]==bytes.fromhex('cd42f9')
    out=ROOT/'build/pride-actor-bounds-original';out.mkdir(exist_ok=True)
    report={'result':'PASS','scope':__doc__,'protocol':'chase-and-return','pre_contact_index':220,
            'native_enemy_bounds':native_box,'md_enemy_bounds':external_box,
            'native_cached_player_bounds':native_player,'md_player_bounds':external_player,
            'native_contact':False,'md_contact':True,'world_positions_equal':True,
            'source_sha256':{'native_ram':hashlib.sha256(source.read_bytes()).hexdigest(),
                             'original_md_capture':hashlib.sha256(original_path.read_bytes()).hexdigest()}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original lizard bounds right483/485 vs player left485 explain earlier inclusive MD contact PASS',flush=True)


if __name__=='__main__':main()
