"""Bind attack control-flow fixtures to original stream data and active actors."""
import csv
import json
from pathlib import Path
import struct
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-attack-evidence';out.mkdir()
    fixture_path=ROOT/'build/pride-porcupine-attack2/report.json'
    md_path=ROOT/'build/md-porcupine-attack/report.json'
    fixtures=bound(fixture_path);capture=bound(md_path)
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    metadata_path=ROOT/'tools/pride_npc_pairs.json'
    pairs={int(r['snes'],16):int(r['md'],16) for r in json.loads(metadata_path.read_text())['pairs']}
    a=0x288cc;b=md.find(bytes.fromhex('030b4a24030b4a5c030b4a94'),0xb8ac2,0xb8b26)
    assert b>=0
    md_start=b;tokens=[];flag_at=None
    while snes[a]!=255:
        if snes[a]==250:
            assert snes[a+1]==1 and flag_at is None
            flag_at=len(tokens);a+=2;continue
        assert snes[a]<128 and md[b]<128
        sp=int.from_bytes(snes[a+1:a+4],'little');mp=int.from_bytes(md[b+1:b+4],'big')
        tokens.append(dict(native_pc=hex(0xc00000+a),md_pc=hex(b),duration=snes[a],
                           native_pose=hex(sp),md_pose=hex(mp),mapped=pairs.get(sp)==mp,
                           durations_equal=snes[a]==md[b]))
        a+=4;b+=4
    native_loop=int.from_bytes(snes[a+1:a+4],'little');md_loop=int.from_bytes(md[b+1:b+4],'big')
    native_samples=[];native_paths=[]
    for field in range(1380,1541,4):
        path=ROOT/f'build/native-pickup-flight/hl_wram_{field}.bin'
        ram=path.read_bytes();native_paths.append(path)
        w=lambda at:struct.unpack_from('<H',ram,at)[0]
        ptr=lambda at:int.from_bytes(ram[at:at+3],'little')
        at=w(0x76);seen=set();previous=0
        while at:
            assert 0x8000<=at<=0xff80 and at not in seen and len(seen)<80 and w(at)==previous
            seen.add(at)
            if ptr(at+0x30)==0xc15b87:
                native_samples.append(dict(field=field,actor=hex(at),descriptor=hex(ptr(at+4)),
                    timer=w(at+0x2c),wait=w(at+0x1c),contact_enabled=w(at+0x2e),
                    persistent=w(at+0x22),x=w(at+8),y=w(at+10),pose=hex(ptr(w(at+12)+10))))
            previous,at=at,w(at+2)
    rows=list(csv.DictReader((md_path.parent/'calls.csv').open()))
    attacks=[r for r in rows if r['pc']=='19a446' and r['action']=='19a446']
    checks=dict(original_cpu_matrix=fixtures['result']=='PASS' and len(fixtures['checks'])==1416,
                ordinary_md_calls=capture['result']=='PASS' and capture['calls']==219,
                all25_poses_mapped=len(tokens)==25 and all(r['mapped'] for r in tokens),
                all25_durations_equal=all(r['durations_equal'] for r in tokens),
                native_contact_flag_after20_poses=flag_at==20,
                native_loops_last_pose=native_loop==0xc00000+a-4,
                md_loops_last_pose=md[b]==255 and md_loop==b-4,
                native_active_attack_observed=bool(native_samples),
                native_delayed_contact_flag=any(r['timer']==22 and r['contact_enabled']==0 for r in native_samples)
                    and any(r['timer']==18 and r['contact_enabled']==1 for r in native_samples),
                md_approach_and_contact_observed=any(r['timer']=='29' for r in attacks)
                    and any(r['pc']=='19a548' and r['timer']=='28' for r in rows))
    paths=[Path(__file__),fixture_path,md_path,metadata_path,*native_paths]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                tokens=tokens,md_stream=hex(md_start),native_contact_flag_after_pose_count=flag_at,
                native_samples=native_samples,native_sample_interval=4,
                original_native_samples_not_per_instruction_execution=True,
                fixture_external_services_intercepted=True,complete_trajectory_or_collision_equivalence=False,
                runtime_adapter_enabled=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                rom_sha256={'snes':digest(ROOT/'Lion King, The (USA).sfc'),'md':digest(ROOT/'Lion King, The (World).md')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),len(native_samples),'active native samples',flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
