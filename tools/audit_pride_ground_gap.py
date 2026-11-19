"""Resolve the immediate cause of the later jump-path gap without tuning physics."""
import csv
import json
from pathlib import Path
import re
import struct

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_actor_bounds_audit import bounds,overlap
from summarize_pride_practice import bound


def main():
    out=ROOT/'build/pride-ground-gap';md=bound(out/'md/report.json');checks={}
    a=json.loads((out/'native/early-audit.json').read_text());b=json.loads((out/'native-lle/early-audit.json').read_text())
    checks['current_engine_gap_reproduced']=a['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe') and a['matched_initial_nonlag_integer_position_updates']==686 and a['first_nonlag_gap']==dict(native_frame=1631,md_frame=2015,native_xy=[607,719],md_xy=[607,714])
    checks['lle_gap_identical']=b['first_nonlag_gap']==a['first_nonlag_gap'] and b['matched_initial_nonlag_integer_position_updates']==686
    for field in (1629,1630,1631,1632):checks[f'full_wram_{field}_aot_lle']=(out/f'native/hl_wram_{field}.bin').read_bytes()==(out/f'native-lle/hl_wram_{field}.bin').read_bytes()
    data={name:path.read_bytes() for name,path in dict(native=out/'native/hl_wram_1630.bin',after=out/'native/hl_wram_1631.bin',md=out/'md/wram-2014.bin',enemy=out/'md/wram-2013.bin').items()}
    def w(name,at):return struct.unpack_from('<H',data[name],at)[0]
    def chain(name,head):
        found=[];at=head
        while at:
            assert at not in found and len(found)<100 and at+128<=len(data[name])
            found.append(at);next_at=w(name,at+2)
            if next_at:assert w(name,next_at)==at
            at=next_at
        return found
    native_active=chain('native',0xb213);md_active=chain('md',0x934e)
    checks['actual_md_contact_is_active']=0x9ace in md_active and (w('md',0x93f2)<<16|w('md',0x93f4))==0xffff9ace
    checks['held_left_no_jump']=[r['pad'] for r in md['frames'] if 2013<=r['field']<=2015]==[64]*3 and w('native',0x5a)==0x200
    checks['same_pre_gap_player_position']=[w('native',0xb21b),w('native',0xb21d)]==[w('md',0x93d6),w('md',0x93d8)]==[609,718]
    checks['same_pre_gap_velocity']=int.from_bytes(data['native'][0xb24f:0xb253],'little')==(w('md',0x940a)<<16|w('md',0x940c))==0x9600
    checks['original_md_contact_flag_only']=data['md'][0x9411]&0x20!=0 and data['native'][0xb256]&0x20==0
    rows=list(csv.DictReader((out/'md/instructions.csv').open()))
    contact=[r for r in rows if r['field']=='2014' and r['type']=='4' and r['address']=='ff9411' and r['pc']=='19a87e']
    kick=[r for r in rows if r['field']=='2015' and r['type']=='4' and r['address']=='ff940a']
    checks['original_contact_sets_bounce']=len(contact)==1 and contact[0]['actor']=='ffff9ace' and int(contact[0]['value'],16)&0x20!=0
    checks['original_rebound_then_gravity']=[(r['pc'],r['value']) for r in kick]==[('197490','fffc0000'),('199322','fffc4e00')]
    checks['native_same_gravity_without_rebound']=int.from_bytes(data['after'][0xb24f:0xb253],'little')==0x9600+0x4e00
    checks['md_same_gravity_after_rebound']=(0xfffc0000+0x4e00)&0xffffffff==next(r['vy'] for r in md['frames'] if r['field']==2015)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native_rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    checks['original_md_rebound_constant']=rom[0x197488:0x197490]==bytes.fromhex('237cfffc0000003c')
    checks['original_snes_same_rebound_constant']=native_rom[0x36740:0x36750]==bytes.fromhex('a90000a03c009700a9fcffa03e009700')
    mapping_path=ROOT/'engine/generated/resources/pride_hitbox_map.h'
    mapping={int(x,16):int(y,16) for x,y in re.findall(r'\{0x([0-9a-f]+),0x([0-9a-f]+),[0-3]\}',mapping_path.read_text())}
    def body(name,actor):
        draw=w(name,actor+12);attributes=w(name,draw+8)
        pose=((w(name,draw+10)<<16|w(name,draw+12))&0xffffff) if name in ('md','enemy') else int.from_bytes(data[name][draw+10:draw+13],'little')&0x3fffff
        if name not in ('md','enemy'):attributes=((attributes&0x40)<<5)|((attributes&0x80)<<5);pose=mapping[pose]
        return bounds(rom,pose,w(name,actor+8),w(name,actor+10),attributes,True)
    player=body('native',0xb213);checks['selected_player_bounds_equal']=player==body('md',0x93ce)
    enemies=[]
    for actor in native_active:
        if actor!=0xb213 and w('native',actor+68) in (10,11,14):
            box=body('native',actor);enemies.append(dict(actor=actor,xy=[w('native',actor+8),w('native',actor+10)],box=box,overlaps=overlap(player,box)))
    checks['no_nearby_native_lizard_porcupine_body_contact']=len(enemies)==6 and not any(e['overlaps'] for e in enemies)
    checks['md_live_lizard_precontact_overlaps']=overlap(body('enemy',0x93ce),body('enemy',0x9ace))
    trace=(out/'native-opcodes.txt').read_text();checks['native_rebound_branch_not_taken']='C3665A ' not in trace and 'C3671D ' not in trace and 'C387EC ' in trace
    paths=[Path(__file__),out/'md/report.json',out/'native/early-audit.json',out/'native-lle/early-audit.json',ROOT/'tools/pride_md_controller_route.py',ROOT/'tools/pride_actor_bounds_audit.py',mapping_path,ROOT/'engine/build-win/tlk_headless.exe',ROOT/'tools/snes_disassemble.py',ROOT/'tools/md_disassemble.py']
    artifacts=[p for p in out.rglob('*') if p.is_file() and p.name!='audit.json']
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,immediate_trigger_proven=all(checks.values()),
        native_active=native_active,original_md_active=md_active,player_selected_md_bounds=player,native_lizards_porcupines=enemies,
        original_md_precontact_lizard_box=body('enemy',0x9ace),
        explanation='Original MD lizard contact sets the cub bounce flag at2014; original rebound at2015 resets vy to-4 before the shared0x4e00 gravity increment. Native lacks that contact and keeps falling.',
        next_work='Trace the lizard birth, movement/action and active-list history that produces the different contact; do not tune cub gravity to hide it.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in artifacts},
        full_movement_or_enemy_equivalence_proven=False,full_first_level_fidelity_complete=False,public_player_changed=False)
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
