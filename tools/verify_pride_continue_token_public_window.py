"""Inspect the packaged launcher's own resource-tree window without desktop input."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32, window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    base = ROOT/'build/pride-continue-token47'
    out = base/'game-window-verification'; out.mkdir()
    package_path = ROOT/'dist/installed-preview47/package-report.json'; bound(package_path)
    trace = out/'tree.jsonl'
    settings = out/'settings';settings.mkdir()
    for before,after in [('host.ini','game.ini'),('resources.ini','resources.ini')]:shutil.copyfile(base/'full-route/aot'/before,settings/after)
    powershell = Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    cmd = [str(powershell), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'scripts/RunInstalledPreview.ps1'),
           '-DataDirectory', str(ROOT/'game-data'),
           '-SettingsDirectory', str(settings), '-Frames', '6000', '-NoAudio', '-InputTape',
           str(ROOT/'build/pride-restart-difficulty25/wide-completion/ordinary.polled.tape')]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['PATH'] = str(Path(os.environ['SystemRoot'])/'System32')
    env['TLK_SOFT_TREE_LOG'] = str(trace)
    checks = {}; hwnd = None; row = None; child = None
    USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline = time.monotonic()+60
            while not child and proc.poll() is None and time.monotonic() < deadline:
                query = f"Get-CimInstance Win32_Process -Filter 'ParentProcessId = {proc.pid}' | Where-Object Name -eq 'LionKing.exe' | Select-Object -ExpandProperty ProcessId"
                output = subprocess.check_output([str(powershell), '-NoProfile', '-Command', query], env=env,
                                                 creationflags=subprocess.CREATE_NO_WINDOW, timeout=10).decode().strip()
                if output: child = int(output.splitlines()[0])
            assert child, 'Packaged player child did not start'
            while not hwnd and proc.poll() is None and time.monotonic() < deadline:
                hwnd = window_for(child); time.sleep(.02)
            assert hwnd
            def wait(predicate):
                while proc.poll() is None and time.monotonic() < deadline:
                    current = latest(trace)
                    if current and predicate(current): return current
                    time.sleep(.02)
                raise AssertionError(('UI timeout', latest(trace)))
            before = wait(lambda r: r['field'] >= 2520)
            profile_hash = digest(settings/'resources.ini')
            capture_client(hwnd, out/'game.png')
            scan = USER32.MapVirtualKeyW(0x7b, 0)
            assert USER32.PostMessageW(hwnd, 0x100, 0x7b, 1+(scan<<16))
            assert USER32.PostMessageW(hwnd, 0x101, 0x7b, 0xc0000001+(scan<<16))
            row = wait(lambda r: r['about'] == 2)
            time.sleep(.2); capture_client(hwnd, out/'resources.png')
            checks['resource_tree_opens_from_real_f12'] = row['about'] == 2
            hud = next(r for r in row['choices'] if r[0] == 'graphics.hud.frames')
            checks['prepared_hud_choice_active_md'] = hud[-1] == 2
            checks['continue_token_choices_active_md'] = all(next(r for r in row['choices'] if r[0]=='graphics.sprites.pickups.continue_token.'+part)[-1]==2 for part in ('frames','palette'))
            checks['profile_not_changed_by_opening_tree'] = digest(settings/'resources.ini') == profile_hash
        finally:
            if hwnd: USER32.PostMessageW(hwnd, 0x10, 0, 0)
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired: proc.terminate(); proc.wait(timeout=5)
    checks['clean_launcher_exit'] = proc.returncode == 0
    command_folder = base/'cmd-verification2'
    checks['actual_cmd_entrypoint_dumped_window'] = (command_folder/'window.png').exists() and 'resource_cache=loaded' in (command_folder/'settings/last-launch.log').read_text()
    paths = [Path(__file__), base/'publication/report.json', package_path, ROOT/'scripts/RunInstalledPreview.ps1', ROOT/'Play Installed Preview.cmd']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
                  process_child=child, tree=row, operating_only_own_child_window=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
