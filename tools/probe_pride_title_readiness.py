"""Research-only title-menu retiming; no maintained runtime or save-policy change."""
import csv
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound
from verify_windows import hashes, pixels
from verify_pride_final_scene_runtime import pcm


def absolute_includes(text, parent):
    return re.sub(r'#include "([^\"]+)"', lambda m: '#include "' + (parent / m[1]).resolve().as_posix() + '"'
                  if (parent / m[1]).is_file() else m[0], text)


def main():
    out = ROOT / 'build/pride-title-readiness-probe3'
    out.mkdir()
    prior = ROOT / 'build/pride-title-upload16'
    build = bound(prior / 'build-report.json')
    old = bound(prior / 'verification/report.json')
    bound(ROOT / 'build/pride-title-readiness-original/report.json')
    frontend = out / 'frontend'
    shutil.copytree(prior / 'frontend', frontend)
    front = frontend / 'sdl_main.c'
    text = front.read_text()
    anchor = 'FinalSceneCaptureNative(s_pixels);'
    assert text.count(anchor) == 1
    front.write_text(text.replace(anchor, 'TitleSetupCapture(s_pixels); ' + anchor))
    host = ROOT / 'engine/runner/pride/final/pride_final_host.c'
    runtime = host.parent / 'pride_final_runtime.inc'
    runtime_text = absolute_includes(runtime.read_text(), runtime.parent)
    anchor = 'continue_title_fade_field=now-((now-final_scene_entry)>=TLK_CONTINUE_MENU_TIMEOUT);'
    assert runtime_text.count(anchor) == 1
    runtime_text = runtime_text.replace(anchor, anchor + '\n        title_probe_ready_field=title_probe_input_field=continue_title_fade_field+191;\n        title_probe_previous_pad=FinalWord(0x5c);')
    runtime_copy = out / 'runtime.inc'
    runtime_copy.write_text(runtime_text)
    observer = ROOT / 'tools/pride_title_readiness_observer.inc'
    text = observer.read_text()
    text = text.replace('0xc463fc,0xc465c0', '0xc0a073,0xc463fc,0xc465c0')
    anchor = 'static void TitleReadyPoint(CpuState *cpu,uint32_t pc) {TitleReadyRow("point",cpu,pc);}'
    assert text.count(anchor) == 1
    hook = r'''
/* Experimental phase4 -> original phase5 constructor. Deliberately not saved:
 * these research runs start from the original backend fixture, never cold-load. */
static void TitleReadyPoint(CpuState *cpu,uint32_t pc) {
    if(pc==0xc0a073 && title_probe_pad_pending &&
       (unsigned)snes_frame_counter+1>=title_probe_input_field) {
        if(FinalWord(0x1ff9e) || FinalAddress(0xdf)!=0xc005ab)exit(118);
        ReloadFastWord(0x5c,title_probe_previous_pad);
        title_probe_pad_pending=0;
        TitleReadyRow("restore",cpu,pc);
    }
    if(pc==0xc463fc && title_probe_ready_field && continue_transition_mode &&
       final_scene_entry && final_scene_have_target && !continue_title_pending &&
       !continue_transition.confirmed_field && !reload_fast_used &&
       FinalAddress(0xdf)==0xc005ab && FinalWord(0x1ff9e)==14 &&
       (unsigned)snes_frame_counter+1>=title_probe_ready_field-3) {
        unsigned actor=FinalWord(0x68);
        if(cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || !cpu->D ||
           actor<0x2000 || actor>0xffa0 || FinalWord(cpu->D)!=actor ||
           FinalAddress(actor+0x30)!=0xc462f6 || FinalWord(actor+0x2e)!=4)exit(117);
        /* Exact phase4 exit fields from C4657E..C465AC. The constructor below
         * owns its child allocation, UI planes, menu and pad-history handling. */
        ReloadFastWord(actor+0x34,0);ReloadFastWord(actor+0x36,0);
        ReloadFastWord(actor+0x1c,0x77);ReloadFastWord(actor+0x1e,0x1e);
        ReloadFastWord(actor+0x2c,12);ReloadFastWord(actor+0x2e,5);
        TitleReadyRow("retime",cpu,pc);
        title_probe_ready_field=0;
        title_probe_pad_pending=1;
        interp_bridge_pre_opcode_redirect(0xc465c0);
    }
    TitleReadyRow("point",cpu,pc);
}
'''
    observer_copy = out / 'observer.inc'
    observer_copy.write_text(text.replace(anchor, hook))
    text = absolute_includes(host.read_text(), host.parent)
    assert text.count(runtime.as_posix()) == 1
    text = text.replace(runtime.as_posix(), runtime_copy.as_posix())
    source = out / 'host.c'
    source.write_text('#include <stdint.h>\nstatic unsigned title_probe_ready_field,title_probe_input_field,title_probe_previous_pad,title_probe_pad_pending;\nstatic void TitleSetupCapture(const uint8_t *);\n'
                      + text + '\n#include "' + observer_copy.as_posix() + '"\n')
    cmd = build['compiles']['host'].copy()
    obj = out / 'host.obj'
    for flag, value in [('-c', source), ('-o', obj), ('-MF', out / 'host.d'), ('-MT', obj)]:
        cmd[cmd.index(flag) + 1] = str(value)
    i = next(i for i, value in enumerate(cmd) if value.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
    cmd[i] = '-DTLK_PRIDE_FRONTEND_SOURCE="' + (frontend / 'sdl_main.c').as_posix() + '"'
    cwd = ROOT / 'build/pride-final-standalone'
    with (out / 'compile.log').open('wb') as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    inputs = argv('link ' + (prior / 'link.rsp').read_text())[1:]
    inputs[inputs.index((prior / 'host.obj').as_posix())] = obj.as_posix()
    rsp = out / 'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    with (out / 'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@' + str(rsp), '-o', str(out / 'player.exe')], cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    shutil.copyfile(prior / 'genesis_plus_gx_libretro.dll', out / 'genesis_plus_gx_libretro.dll')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['TLK_FINAL_MD_ART'] = '1'
    checks = {}; commands = {}; observations = {}
    (out / 'host.ini').write_text('opengl = 0\nscale = 2\n')
    base_tape = Path(old['commands']['256-normal700'][old['commands']['256-normal700'].index('--input') + 1]).read_bytes()
    # Input tapes are indexed in absolute backend fields, including this fixture's 4444 origin.
    def run(width, label, end, start=None, release=None, button=0x1000):
        folder = out / f'{width}-{label}'; folder.mkdir()
        tape = bytearray(base_tape)
        if len(tape) < 2 * (4444 + end + 2):tape.extend(bytes(2 * (4444 + end + 2) - len(tape)))
        if start is not None:
            for age in range(start, (release if release is not None else start) + 1):
                struct.pack_into('<H', tape, (4444 + age - 1) * 2, button)
        tape_path = folder / 'input.tape'; tape_path.write_bytes(tape)
        cmd = old['commands'][f'{width}-normal700'].copy(); cmd[0] = str(out / 'player.exe'); cmd += ['--lle']
        for flag, value in [('--config', out / 'host.ini'), ('--frames', 4444 + end), ('--input', tape_path),
                            ('--dump-window', folder / 'window.png'), ('--dump-scene', folder / 'scene.json'), ('--wav', folder / 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        with (folder / 'run.log').open('wb') as log:
            result = subprocess.run(cmd, cwd=ROOT, env=dict(env, TLK_TITLE_READY_DIR=str(folder)),
                                    stdout=log, stderr=subprocess.STDOUT, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        checks[folder.name + '_exit'] = result.returncode == 0
        commands[folder.name] = cmd
        rows = list(csv.DictReader((folder / 'actor.csv').open()))
        polls = [int(r['age']) for r in rows if r['pc'] == 'c50178']
        retimes = [int(r['age']) for r in rows if r['kind'] == 'retime']
        observations[folder.name] = dict(first_poll=min(polls) if polls else None, retimes=retimes)
        print(folder.name, result.returncode, observations[folder.name], flush=True)
        return folder
    for width in (256, 320):
        neutral = run(width, 'neutral', 700)
        checks[f'{width}_first_poll515'] = observations[neutral.name]['first_poll'] == 515
        checks[f'{width}_one_retime512'] = observations[neutral.name]['retimes'] == [512]
        early = run(width, 'start514', 700, 514)
        ready = run(width, 'start515', 700, 515)
        held = run(width, 'held512to515', 700, 512, 515)
        released = run(width, 'released512to514', 700, 512, 514)
        checks[f'{width}_early_ignored_guest'] = hashes(early / 'run.log') == hashes(neutral / 'run.log')
        checks[f'{width}_early_ignored_client'] = pixels(early / 'window.png') == pixels(neutral / 'window.png')
        checks[f'{width}_ready_changes_guest'] = hashes(ready / 'run.log') != hashes(neutral / 'run.log')
        checks[f'{width}_ready_changes_client'] = pixels(ready / 'window.png') != pixels(neutral / 'window.png')
        checks[f'{width}_held_accepted_client'] = pixels(held / 'window.png') == pixels(ready / 'window.png')
        checks[f'{width}_held_accepted_guest'] = hashes(held / 'run.log') == hashes(ready / 'run.log')
        checks[f'{width}_released_ignored_guest'] = hashes(released / 'run.log') == hashes(neutral / 'run.log')
        checks[f'{width}_released_ignored_client'] = pixels(released / 'window.png') == pixels(neutral / 'window.png')
        run(width, 'menu515', 515)
        run(width, 'newgame1115', 1115, 515)
    paths = [Path(__file__), observer, runtime, host, prior / 'build-report.json', prior / 'verification/report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands, observations=observations,
                  research_only=True, serialized_readiness=False, compiled_mode_verified=False,
                  binary_sha256=digest(out / 'player.exe'),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix(): digest(cwd/p) for p in inputs if not p.startswith('-')},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k,v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
