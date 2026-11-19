"""Exercise the packaged manifest launcher with a clean DLL search path."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-sprite-fresh44'
    out = base/'launcher-verification'; out.mkdir()
    package_path = ROOT/'dist/installed-preview44/package-report.json'
    bound(package_path)
    setup_path = base/'setup-verification/report.json'; setup = bound(setup_path)
    assert setup['result'] == 'PASS'
    data = base/'setup-verification/Data & installed assets'
    original = base/'setup-verification/warm'
    settings = out/'Settings & recordings'; settings.mkdir()
    for source, name in [('host.ini', 'game.ini'), ('resources.ini', 'resources.ini')]:
        shutil.copy2(original/source, settings/name)
    (settings/'last_session.rec').write_bytes(b'preserve existing user recording')
    protected = {p.name: digest(p) for p in settings.iterdir()}
    powershell = Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    clean['PATH'] = str(Path(os.environ['SystemRoot'])/'System32')
    commands = {}; checks = {}
    def run(label, installed, config, extra=()):
        folder = out/label; folder.mkdir()
        cmd = [str(powershell), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'scripts/RunInstalledPreview.ps1'),
               '-DataDirectory', str(installed), '-SettingsDirectory', str(config), *map(str, extra)]
        commands[label] = cmd
        with (folder/'run.log').open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=clean, stdout=log, stderr=subprocess.STDOUT,
                                timeout=180, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label, rc, flush=True)
        return folder, rc
    # Preserve pre-existing choices and recordings while verifying actual playback.
    tape = Path(setup['commands']['warm'][setup['commands']['warm'].index('--input-polled')+1])
    folder, rc = run('playback', data, settings, ['-Frames', 1600, '-InputTape', tape, '-NoPace', '-NoAudio',
        '-WindowCapture', out/'playback/window.png', '-SceneCapture', out/'playback/scene.json', '-AudioCapture', out/'playback/audio.wav'])
    checks['packaged_clean_path_playback'] = rc == 0
    checks['same_guest'] = hashes(settings/'last-launch.log') == hashes(original/'run.log')
    for name in ('window.png', 'scene.json', 'audio.wav'):
        checks[name+'_exact'] = digest(folder/name) == digest(original/name)
    checks['settings_and_recording_preserved'] = all(digest(settings/name) == sha for name, sha in protected.items())
    checks['uses_installed_cache_and_audio_backend'] = all(s in (settings/'last-launch.log').read_text()
        for s in ('resource_cache=loaded', 'MD audio ready'))
    # A new settings directory receives defaults only once.
    defaults = out/'New settings'
    folder, rc = run('defaults', data, defaults, ['-Frames', 1, '-NoPace', '-NoAudio'])
    checks['creates_default_settings'] = rc == 0 and (defaults/'game.ini').exists() and (defaults/'resources.ini').read_bytes() == (ROOT/'profiles/pride-development-preview.ini').read_bytes()
    for label in ('missing-manifest', 'old-installation', 'damaged-hud', 'escaped-path', 'missing-sprites', 'old-sprites', 'damaged-sprites', 'escaped-sprites'):
        installed = out/label/'data'; installed.parent.mkdir()
        if label != 'missing-manifest':
            shutil.copytree(data, installed)
            info = json.loads((installed/'install.json').read_text())
            if label == 'missing-sprites': del info['sprite_assets']
            elif label == 'old-sprites': info['sprite_assets']['version'] = 0
            elif label == 'escaped-sprites': info['sprite_assets']['file'] = '../outside.assets'
            elif label == 'damaged-sprites':
                p = installed/info['sprite_assets']['file']; raw = bytearray(p.read_bytes()); raw[-1] ^= 1; p.write_bytes(raw)
            elif label == 'old-installation': del info['hud_assets']
            elif label == 'damaged-hud':
                hud = installed/info['hud_assets']['file']; raw = bytearray(hud.read_bytes()); raw[-1] ^= 1; hud.write_bytes(raw)
            else: info['hud_assets']['file'] = '../outside.assets'
            (installed/'install.json').write_text(json.dumps(info, indent=2)+'\n')
        config = installed.parent/'must-not-be-created'
        # run() owns a separate log folder so fixture bytes remain explicit.
        folder, rc = run(label+'-check', installed, config, ['-Frames', 1, '-NoPace', '-NoAudio'])
        checks[label+'_rejects_before_settings_or_game'] = rc == 8 and not config.exists() and 'Setup.cmd' in (folder/'run.log').read_text()
    package = ROOT/'dist/installed-preview44'
    checks['packaged_binary_exact'] = digest(package/'LionKing.exe') == json.loads((base/'build-report.json').read_text())['binary_sha256']
    def game_payload(path):
        with path.open('rb') as stream: magic = stream.read(8)
        return (path.suffix.lower() in ('.sfc', '.smc', '.bin', '.assets', '.cache') or
                magic in (b'TLKSPR01', b'TLKHUD01', b'TLKSCN01', b'TLKFMAR1', b'TLKFNAT1', b'TLKTBK01') or
                (path.stat().st_size == 3145728 and digest(path) in (
                    '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712',
                    'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')))
    checks['no_rom_or_prepared_game_data_in_package'] = not any(game_payload(p) for p in package.rglob('*') if p.is_file())
    paths = [Path(__file__), package_path, setup_path, ROOT/'scripts/RunInstalledPreview.ps1',
             ROOT/'Play Installed Preview.cmd', ROOT/'profiles/pride-development-preview.ini',
             package/'licenses/NOTICE-fonts.md']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  cleaned_path=clean['PATH'], existing_public_previews_preserved=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
