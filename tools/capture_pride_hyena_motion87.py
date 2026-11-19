"""Original boss motion parameters from preserved native snapshots and ordinary MD replay.

Run with the32-bit research Python. Different recorded routes are not paired
physics fixtures; this identifies their actual launch variants before comparison.
"""
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab
from pride_arena_history import bound


def signed32(v):return v-(1<<32) if v&(1<<31) else v


def episodes(rows):
    result=[]
    for row in rows:
        if not result or row['action']!=result[-1]['action'] or row['field']!=result[-1]['last_field']+1:
            result.append(dict(action=row['action'],first_field=row['field'],last_field=row['field'],fields=0,
                               first_position=[row['x'],row['y']],first_velocity_q16=[row['vx_q16'],row['vy_q16']]))
        result[-1].update(last_field=row['field'],fields=result[-1]['fields']+1,
                          last_position=[row['x'],row['y']],last_velocity_q16=[row['vx_q16'],row['vy_q16']])
    return result


def main():
    out=ROOT/'build/pride-hyena-motion87';out.mkdir();checks={};paths=[Path(__file__)];cases={}
    for source in ('snes','md'):
        original=ROOT/'build/pride-hyena-recovery'/source/'report.json';bound(original);paths.append(original)
        for difficulty in ('normal','hard'):
            folder=out/source/difficulty;folder.mkdir(parents=True)
            prior=original.parent/difficulty/'frames.json';expected=json.loads(prior.read_text());paths.append(prior)
            rows=[];matched=[];descriptors=set()
            if source=='snes':
                actor=0xba13
                for ref in expected:
                    file=prior.parent/f"hl_wram_{ref['field']}.bin";ram=file.read_bytes();paths.append(file)
                    word=lambda a:struct.unpack_from('<H',ram,a)[0]
                    pointer=lambda a:int.from_bytes(ram[a:a+3],'little')
                    draw=word(actor+12);descriptors.add(pointer(actor+4))
                    actual=dict(field=ref['field'],health=word(actor+0x2a),cycle=word(actor+0x28),timer=word(actor+0x2c),
                                tag=word(actor+0x2e),action=pointer(actor+0x30),pose=pointer(draw+10),x=word(actor+8),y=word(actor+10),
                                facing=word(actor+0x20),player_health=word(0x2004),lives=word(0x1ffaa))
                    matched.append(actual==ref)
                    actual.update(vx_q16=signed32(int.from_bytes(ram[actor+0x38:actor+0x3c],'little')),
                                  vy_q16=signed32(int.from_bytes(ram[actor+0x3c:actor+0x40],'little')))
                    rows.append(actual)
                checks[difficulty+'_native_owned_descriptor']=descriptors=={0xc58c68}
            else:
                plan=ROOT/f'build/pride-md-hyena-{difficulty}-repeat-plan/report.json';bound(plan);paths.append(plan)
                tape=plan.parent/'selected-inputs.json';pads=json.loads(tape.read_text());paths.append(tape)
                targets={row['field']:row for row in expected};game=MdLab()
                game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
                for port in (0,1):game.core.retro_set_controller_port_device(port,513)
                actor=0x9a4e
                try:
                    for field,pad in enumerate(pads[:max(targets)],1):
                        game.step(pad);game.samples.clear()
                        if field not in targets:continue
                        word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                        longword=lambda a:word(a)<<16|word(a+2)
                        draw=word(actor+12);descriptors.add(longword(actor+4)&0xffffff)
                        actual=dict(field=field,health=word(actor+0x2a),cycle=word(actor+0x28),timer=word(actor+0x2c),
                                    tag=word(actor+0x2e),action=longword(actor+0x30)&0xffffff,
                                    pose=longword(draw+10)&0xffffff,x=word(actor+8),y=word(actor+10),
                                    facing=word(actor+0x20),player_health=word(0xccf6),lives=word(0xccee))
                        matched.append(actual==targets[field])
                        actual.update(vx_q16=signed32(longword(actor+0x38)),vy_q16=signed32(longword(actor+0x3c)))
                        rows.append(actual)
                finally:game.close()
                checks[difficulty+'_md_stable_descriptor']=len(descriptors)==1
            checks[source+'_'+difficulty+'_all_prior_fields_exact']=len(rows)==len(expected) and all(matched)
            (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n')
            states=episodes(rows);(folder/'episodes.json').write_text(json.dumps(states,indent=2)+'\n')
            windup=0xc148b6 if source=='snes' else 0x19ba8c
            launch=[dict(field=r['first_field'],velocity_q16=r['first_velocity_q16']) for r in states if r['action']==windup]
            cases[source+'-'+difficulty]=dict(fields=len(rows),descriptors=sorted(descriptors),episodes=states,windup_parameters=launch)
            print(source,difficulty,'rows',len(rows),'windup velocities',launch,flush=True)
    paths += [ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md']
    report=dict(result='ORIGINAL_HYENA_MOTION_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                guest_or_rom_edits=False,production_changed=False,
                different_route_state_counts_are_not_a_physics_difference=True,whole_ai_or_motion_equivalence_proven=False,
                next_step='Compare common original motion/launch helpers with matched incoming parameters and contact state; do not patch from raw episode lengths.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
