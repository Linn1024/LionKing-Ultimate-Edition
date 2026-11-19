"""Keep ordinary MD final-life/Continue playback exact across the fresh rebuild."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-sprite-fresh44'
    out = base/'continue-verification'; out.mkdir()
    build_path = base/'build-report.json'; bound(build_path)
    prior_path = ROOT/'build/pride-hud-assets42/build-report.json'; bound(prior_path)
    original_path = ROOT/'build/pride-final-resource2/lifecycle/report.json'
    original = bound(original_path)
    template = original['commands']['ordinary-start-menu'].copy()
    i = template.index('--save-at'); del template[i:i+3]
    assets_path = base/'setup-verification/report.json'
    actual_setup = bound(assets_path)
    assert actual_setup['result'] == 'PASS'
    data = base/'setup-verification/Data & installed assets'
    info = json.loads((data/'install.json').read_text())
    for flag, key in [('--final-menu-assets', 'menu_assets'), ('--final-native-assets', 'native_final_assets'),
                      ('--title-bank-assets', 'title_bank_assets'), ('--hud-assets', 'hud_assets'), ('--sprite-assets', 'sprite_assets')]:
        template += [flag, str(data/info[key]['file'])]
    template += ['--asset-cache', str(data/info['scene_cache']['file'])]
    profile_text = Path(template[template.index('--resource-profile')+1]).read_text()+'\ngraphics.hud = md\n'
    commands = {}; checks = {}
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    def run(label, frames=5300, prior=False, lle=False, save=False, load=None):
        folder = out/label; folder.mkdir(); cmd = template.copy()
        cmd[0] = str(ROOT/'build/pride-hud-assets42/player.exe' if prior else base/'player.exe')
        for flag, value in [('--frames', frames), ('--dump-window', folder/'window.png'),
                            ('--dump-scene', folder/'scene.json'), ('--wav', folder/'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        (folder/'resources.ini').write_text(profile_text)
        for flag, file in [('--config', 'host.ini'), ('--resource-profile', 'resources.ini')]:
            cmd[cmd.index(flag)+1] = str(folder/file)
        cmd += ['--hash-at', ','.join(map(str, range(1, frames+1)))]
        if prior:
            i = cmd.index('--sprite-assets'); del cmd[i:i+2]
        if lle: cmd.append('--lle')
        if save: cmd += ['--save-at', '3800', str(folder/'saved.state')]
        if load: cmd += ['--load', str(load)]
        env = dict(clean, TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        commands[label] = cmd
        with (folder/'run.log').open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=240, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit'] = rc == 0
        print(label, rc, flush=True)
        return folder
    control = run('prior42', prior=True, save=True)
    aot = run('fresh-aot'); lle = run('fresh-lle', lle=True)
    cold = run('cold-aot', load=control/'saved.state')
    cold_lle = run('cold-lle', lle=True, load=control/'saved.state')
    menu = run('fresh-menu', frames=3920, load=control/'saved.state')
    old_menu = run('prior-menu', frames=3920, prior=True, load=control/'saved.state')
    pattern = r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows = lambda folder: re.findall(pattern, (folder/'run.log').read_text())
    for label, left, right in [('prior', control, aot), ('modes', aot, lle), ('cold_modes', cold, cold_lle), ('menu', menu, old_menu)]:
        checks[label+'_guest'] = hashes(left/'run.log') == hashes(right/'run.log')
        checks[label+'_all_sampled_fields'] = rows(left) == rows(right)
        for file in ('window.png', 'scene.json', 'audio.wav'):
            checks[label+'_'+file] = digest(left/file) == digest(right/file)
    checks['all5300_warm_fields'] = len(rows(aot)) == len(rows(control)) == 5300
    checks['cold_all1500_fields'] = len(rows(cold)) == 1500 and rows(cold) == [r for r in rows(aot) if int(r[0]) > 3800]
    checks['cold_remaining_pcm'] = pcm(cold/'audio.wav') == pcm(aot/'audio.wav')[-len(pcm(cold/'audio.wav')):]
    checks['cold_final_picture'] = digest(cold/'window.png') == digest(aot/'window.png')
    final = json.loads((aot/'tree.jsonl').read_text().splitlines()[-1])
    checks['continued_playable_pride'] = final['level'] == 0 and final['health'] > 0 and final['lives'] == 2
    paths = [Path(__file__), build_path, prior_path, original_path, assets_path]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  ordinary_poweron_controller_route=True, guest_or_rom_edits=False,
                  menu_art_source='native as advertised by the final-life leaf',
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
