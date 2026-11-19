"""Execute complete original walking continuations on preserved scene snapshots.

Run with .tools/python32/python.exe. Roar strength is an explicit fixture input;
these isolated calls do not establish an ordinary port walking response.
"""
import csv
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab
from pride_arena_history import bound


def main():
    out = ROOT / 'build/pride-porcupine-walk-originals'
    out.mkdir()
    core = ROOT / 'engine/snesrecomp/runner/src/snes'
    runtime = ROOT / 'engine/build-win/tlk-runtime/interp816.c'
    source = ROOT / 'tools/pride_porcupine_walk_oracle.c'
    command = ['C:/mingw32/bin/gcc.exe', '-O2', '-shared', '-static-libgcc',
               '-I'+str(core), str(source), str(runtime), '-o', str(out/'oracle.dll')]
    subprocess.run(command, check=True, cwd=ROOT)
    rom = read_rom('Lion King, The (USA).sfc',
                   '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    native = C.CDLL(str(out/'oracle.dll'))
    native.terrain_native_init.argtypes = [C.c_void_p, C.c_uint]
    assert native.terrain_native_init(C.create_string_buffer(rom), len(rom))
    native.porcupine_walk_native.argtypes = [C.c_void_p, C.c_uint, C.c_uint,
                                           C.c_uint, C.POINTER(C.c_uint), C.c_void_p]
    paths = [Path(__file__), source, runtime, core/'interp816.h',
             ROOT/'tools/pride_terrain_native_oracle.c', ROOT/'tools/md_lab.py']
    cases = []
    checks = {}
    for frame, actor in ((2892, 0xb593), (2940, 0xb593), (2980, 0xb593), (3060, 0xb893)):
        path = ROOT/f'build/native-pickup-flight/hl_wram_{frame}.bin'
        paths.append(path)
        data = path.read_bytes()
        word = lambda a: int.from_bytes(data[a:a+2], 'little')
        assert int.from_bytes(data[actor+0x30:actor+0x33], 'little') == 0xc150d7
        assert int.from_bytes(data[actor+4:actor+7], 'little') == 0xc58c5c
        for strength in (0, 10, 24):
            raw = (C.c_uint*40)()
            after = C.create_string_buffer(0x20000)
            ok = native.porcupine_walk_native(C.create_string_buffer(data), len(data), actor, strength, raw, after)
            distance = max(abs(word(0xb21b)-word(actor+8)), abs(word(0xb21d)-word(actor+10)))
            reacted = strength-max(0, distance-50)//8 > 10
            values = list(raw)
            label = f'snes-{frame}-{strength}'
            checks[label] = bool(ok) and values[24] == 1 and values[25] == int(reacted) and values[26:28] == [1, 1]
            checks[label+'_continuation'] = (values[16] == (0xc15b87 if reacted else 0xc150d7)
                and values[18] == (27 if reacted else word(actor+0x2c)-1)
                and (not reacted or values[8:13] == [0xc15b87, 0xc288ac, 28, 0, 1])
                and (not reacted or values[17] == 0xc28959))
            (out/(label+'.wram.bin')).write_bytes(after.raw)
            cases.append(dict(source='snes', label=label, distance=distance, strength=strength,
                              responded=reacted, raw=values, pose=hex(values[34])))

    original_path = ROOT/'build/md-porcupine-idle-roar2/report.json'
    original = bound(original_path)
    paths.append(original_path)
    library = original_path.parent/'trace.dll'
    trace = C.CDLL(str(library))
    trace.contact_trace_init.argtypes = [C.c_void_p, C.c_char_p]
    paths += [library, ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    for name in ('3280-32', '3280-80', '3300-56', '3300-80'):
        installed = original['cases'][name]['installed'][0]
        field = int(installed['field'])
        actor = int(installed['actor'], 16)
        tape = original_path.parent/name/'polled.libretro.tape'
        paths.append(tape)
        pads = struct.unpack('<'+'H'*(tape.stat().st_size//2), tape.read_bytes())
        game = MdLab()
        game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
        for port in (0, 1): game.core.retro_set_controller_port_device(port, 513)
        assert trace.contact_trace_init(game.core._handle, str(out/(name+'.calls.csv')).encode())
        index = 0
        try:
            for f in range(1, field):
                trace.contact_trace_field(f)
                game.step(pads[index])
                if trace.contact_trace_polled(): index += 1
            trace.contact_trace_close()
            baseline = bytes(game.work_ram)
            (out/(name+'.before.wram.bin')).write_bytes(baseline)
            def word(at, value=None):
                at &= 65535
                if value is None: return game.work_ram[at] | game.work_ram[at+1]<<8
                game.work_ram[at] = value & 255
                game.work_ram[at+1] = value >> 8 & 255
            def pointer(at, value=None):
                if value is None: return (word(at)<<16 | word(at+2)) & 0xffffff
                word(at, value>>16); word(at+2, value)
            class Map(C.Structure):
                _fields_ = [(k, C.c_void_p) for k in ('base', 'read8', 'read16', 'write8', 'write16')]
            class Prefix(C.Structure):
                _fields_ = [('map', Map*256), ('poll', C.c_uint*3), ('cycles', C.c_int),
                            ('refresh', C.c_int), ('end', C.c_uint), ('dar', C.c_uint*16), ('pc', C.c_uint)]
            cpu = Prefix.in_dll(game.core, 'm68k')
            game.core.m68k_run.argtypes = [C.c_uint]
            for strength in (0, 10, 24):
                C.memmove(C.addressof(game.work_ram), baseline, len(baseline))
                pointer(0x81c4, 0xff0000|actor)
                word(0xccf4, strength)
                player = pointer(0xcd46) & 65535
                distance = max(abs(word(player+8)-word(actor+8)), abs(word(player+10)-word(actor+10)))
                before_timer = word(actor+0x2c)
                before_action = pointer(actor+0x30)
                assert before_action == 0x199ac8, (name, hex(before_action))
                for register in range(16): game.core.m68k_set_reg(register, 0)
                game.core.m68k_set_reg(17, 0x2700)
                game.core.m68k_set_reg(15, 0xffe000)
                game.core.m68k_set_reg(16, 0x199ac8)
                pointer(0xe000, 0x4000)
                seen = dict(helper=0, constructor=0, animation=0, cue=0)
                constructor = None
                for n in range(100000):
                    pc = game.core.m68k_get_reg(16) & 0xffffff
                    assert cpu.pc & 0xffffff == pc
                    if pc == 0x4000: break
                    for key, address in [('helper', 0x19a086), ('constructor', 0x19a04a),
                                         ('animation', 0x2ce6), ('cue', 0x19a594)]:
                        if pc == address: seen[key] += 1
                    if pc == 0x19a07e:
                        constructor = [pointer(actor+0x30), pointer(actor+0xe), word(actor+0x2c),
                                       word(actor+0x2e), word(actor+0x22)]
                    game.core.m68k_run(cpu.cycles+1)
                else: raise AssertionError(('MD did not return', name, hex(pc)))
                reacted = strength-max(0, distance-50)//8 > 10
                final = [pointer(actor+0x30), pointer(actor+0xe), word(actor+0x2c),
                         word(actor+0x2e), word(actor+0x22)]
                label = f'md-{name}-{strength}'
                checks[label] = (seen == dict(helper=1, constructor=int(reacted), animation=1, cue=0)
                    and game.core.m68k_get_reg(15) == 0xffe004)
                checks[label+'_continuation'] = (final[0] == (0x19a446 if reacted else 0x199ac8)
                    and final[2] == (27 if reacted else before_timer-1)
                    and (not reacted or constructor == [0x19a446, 0xb8acc, 28, 0, 1])
                    and (not reacted or final[1] == 0xb8750))
                pose = pointer((word(actor+0xc)&65535)+10)
                cases.append(dict(source='md', label=label, distance=distance, strength=strength,
                                  responded=reacted, constructor=constructor, final=final, calls=seen,
                                  pose=hex(pose), instructions=n))
                (out/(label+'.wram.bin')).write_bytes(bytes(game.work_ram))
        finally:
            trace.contact_trace_close()
            game.close()
    pairs_path = ROOT/'tools/pride_npc_pairs.json'
    paths.append(pairs_path)
    pairs = {int(r['snes'], 16): int(r['md'], 16) for r in json.loads(pairs_path.read_text())['pairs']}
    native_poses = {int(r['pose'], 16) for r in cases if r['source'] == 'snes' and r['responded']}
    md_poses = {int(r['pose'], 16) for r in cases if r['source'] == 'md' and r['responded']}
    checks['response_pose_mapping'] = {pairs.get(p) for p in native_poses} == md_poses and bool(md_poses)
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, cases=cases,
                  compile_command=command, intercepted_callees=[], isolated_snapshot_fixtures=True,
                  guest_fixture_inputs=['current actor', 'scratch/return ABI', 'active roar strength'],
                  ordinary_port_walking_response_proven=False, runtime_changed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks),
          [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
