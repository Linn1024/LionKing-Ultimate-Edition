"""Read guest action/return context at the original roar helper, without edits."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    out = ROOT/'build/pride-walking-guest-context2'; out.mkdir()
    source = ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json'
    template = bound(source)['commands']['full-aot'].copy()
    old_source = ROOT/'build/pride-porcupine-walk-calls-search/report.json'
    prior = bound(old_source)
    tape = ROOT/'build/pride-porcupine-walk-calls-search/neutral.poweron.tape'
    profile = ROOT/'build/pride-porcupine38/idle-roar-full/resources.ini'
    template[template.index('--input-polled')+1] = str(tape)
    i = template.index('--hash-at'); del template[i:i+2]
    script = out/'observe.gdb'
    script.write_text('''set pagination off
set confirm off
break FN_C157E2_M0X0
commands
silent
set $actor=*(unsigned short*)((char*)&g_ram+0x68)
set $guest_s=*(unsigned short*)((char*)&g_cpu+6)
printf "HELPER field=%u actor=%x action=%x strength=%u player_action=%x player_x=%u player_y=%u actor_x=%u actor_y=%u sp=%x ret=%x\\n", *(unsigned int*)&snes_frame_counter, $actor, (*(unsigned int*)((char*)&g_ram+$actor+0x30))&0xffffff, *(unsigned short*)((char*)&g_ram+0xa698), (*(unsigned int*)((char*)&g_ram+0xb243))&0xffffff, *(unsigned short*)((char*)&g_ram+0xb21b), *(unsigned short*)((char*)&g_ram+0xb21d), *(unsigned short*)((char*)&g_ram+$actor+8), *(unsigned short*)((char*)&g_ram+$actor+10), $guest_s, (*(unsigned int*)((char*)&g_ram+$guest_s+1))&0xffffff
continue
end
break FN_C15791_M0X0
commands
silent
set $actor=*(unsigned short*)((char*)&g_ram+0x68)
set $guest_s=*(unsigned short*)((char*)&g_cpu+6)
printf "CONSTRUCTOR field=%u actor=%x action=%x strength=%u sp=%x ret=%x\\n", *(unsigned int*)&snes_frame_counter, $actor, (*(unsigned int*)((char*)&g_ram+$actor+0x30))&0xffffff, *(unsigned short*)((char*)&g_ram+0xa698), $guest_s, (*(unsigned int*)((char*)&g_ram+$guest_s+1))&0xffffff
continue
end
run
''')
    commands = {}; returns = {}
    env = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    for label in ('normal', 'debugger'):
        folder = out/label; folder.mkdir(); cmd = template.copy()
        for flag, value in [('--frames', 3500), ('--dump-window', folder/'window.png'),
                            ('--dump-scene', folder/'scene.json'), ('--wav', folder/'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        for flag, name, original in [('--config','host.ini',ROOT/'build/pride-porcupine38/idle-roar-full/host.ini'),
                                     ('--resource-profile','resources.ini',profile)]:
            p = folder/name; p.write_bytes(original.read_bytes()); cmd[cmd.index(flag)+1] = str(p)
        if label == 'debugger': cmd = ['C:/mingw32/bin/gdb.exe', '--batch', '-x', str(script), '--args', *cmd]
        commands[label] = cmd
        with (folder/'run.log').open('wb') as log:
            returns[label] = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                           timeout=180, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label, returns[label], flush=True)
    text = (out/'debugger/run.log').read_text()
    entries = [dict(re.findall(r'(\w+)=(\w+)', line)) for line in text.splitlines() if line.startswith('HELPER ')]
    checks = dict(normal_exit=returns['normal']==0, debugger_exit=returns['debugger']==0,
                  guest_neutral=hashes(out/'normal/run.log')==hashes(out/'debugger/run.log'),
                  observes_guest_context=bool(entries),
                  walking_action_observed=any(r['action']=='c150d7' for r in entries))
    for name in ('window.png','scene.json','audio.wav'):
        checks[name+'_neutral'] = (out/'debugger'/name).exists() and digest(out/'normal'/name)==digest(out/'debugger'/name)
    paths = [Path(__file__),source,old_source,tape,profile,script,ROOT/'engine/snesrecomp/runner/src/cpu_state.h']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  guest_context=entries, prior_report_result=prior['result'], ordinary_controls_only=True,
                  guest_register_or_memory_writes=False, ordinary_walking_roar_response_proven=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(entries),'helper entries',sorted({r['action'] for r in entries}),flush=True)


if __name__ == '__main__': main()
