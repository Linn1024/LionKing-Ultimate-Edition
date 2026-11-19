"""Exercise actual Setup, damaged-cache rejection, repair and cold continuation."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-installed-cache41'
    build_path = base/'build-report.json'
    bound(build_path)
    out = base/'setup-verification'
    out.mkdir()
    data = out/'Data & installed assets'
    source = base/'verification/report.json'
    verified = bound(source)
    assert verified['result'] == 'PASS'
    template = verified['commands']['full-aot'].copy()
    i = template.index('--hash-at'); del template[i:i+2]
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    commands = {}
    checks = {}
    def setup(label):
        cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'scripts/Setup.ps1'),
               '-SnesRom', str(ROOT/'Lion King, The (USA).sfc'), '-MdRom', str(ROOT/'Lion King, The (World).md'),
               '-DataDirectory', str(data), '-NonInteractive']
        commands[label] = cmd
        with (out/(label+'.log')).open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=clean, stdout=log, stderr=subprocess.STDOUT,
                                timeout=180, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exited'] = rc == 0
        print(label, rc, flush=True)
        return json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    first = setup('setup-first')
    (out/'manifest-first.json').write_text(json.dumps(first, indent=2)+'\n')
    cache = data/first['scene_cache']['file']
    cache_hash = digest(cache)
    checks['setup_cache_matches_candidate_preparation'] = cache_hash == digest(base/'verification/Game data & scene cache/scenes-v1.cache')
    checks['setup_cache_manifest_digest'] = cache_hash == first['scene_cache']['sha256']
    for key, source_name in [('rom', 'snes'), ('md-rom', 'megadrive')]:
        template[template.index('--'+key)+1] = str(data/first['roms'][source_name]['file'])
    for flag, key in [('--final-menu-assets', 'menu_assets'), ('--final-native-assets', 'native_final_assets'),
                      ('--title-bank-assets', 'title_bank_assets')]:
        template[template.index(flag)+1] = str(data/first[key]['file'])
        checks[key+'_prepared_digest'] = digest(data/first[key]['file']) == first[key]['sha256']
    template[template.index('--asset-cache')+1] = str(cache)
    original_tape = Path(template[template.index('--input-polled')+1])
    def run(label, frames, extra=(), tape=None):
        folder = out/label
        folder.mkdir()
        cmd = template.copy()
        for flag, value in [('--frames', frames), ('--dump-window', folder/'window.png'),
                            ('--dump-scene', folder/'scene.json'), ('--wav', folder/'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        for flag, name in [('--config', 'host.ini'), ('--resource-profile', 'resources.ini')]:
            target = folder/name
            target.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
            cmd[cmd.index(flag)+1] = str(target)
        if tape: cmd[cmd.index('--input-polled')+1] = str(tape)
        cmd += list(map(str, extra))
        commands[label] = cmd
        env = clean.copy()
        env.update(TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'), TLK_AUDIO_EVENTS=str(folder/'events.csv'),
                   TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'))
        with (folder/'run.log').open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=180, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label, rc, flush=True)
        return folder, rc, (folder/'run.log').read_text()
    seed, rc, text = run('seed', 1460, ['--save-at', 1460, out/'seed/saved.state'])
    checks['seed_created_from_installed_data'] = rc == 0 and 'resource_cache=loaded' in text and (seed/'saved.state').exists()
    tree = json.loads((seed/'tree.jsonl').read_text().splitlines()[-1])
    assert tree['field'] == 1460
    suffix = out/'remaining.polled.tape'
    suffix.write_bytes(original_tape.read_bytes()[tree['poll_index']*2:])
    warm, rc, text = run('warm', 1600)
    checks['warm_installed_playback'] = rc == 0 and 'resource_cache=loaded' in text
    state_hash = digest(seed/'saved.state')
    original_cache = cache.read_bytes()
    bad = bytearray(original_cache); bad[-1] ^= 1
    cache.write_bytes(bad)
    reject, rc, text = run('damaged-cache-cold', 1600, ['--load', seed/'saved.state'], suffix)
    checks['damaged_cache_rejected_before_saved_guest_load'] = (rc == 8 and 'loaded_state=' not in text
        and 'Cannot load installed game data:' in text and not (reject/'window.png').exists()
        and not (reject/'audio.wav').exists())
    second = setup('setup-repair')
    (out/'manifest-repaired.json').write_text(json.dumps(second, indent=2)+'\n')
    checks['setup_repaired_exact_cache'] = cache.read_bytes() == original_cache
    checks['repair_preserved_save'] = digest(seed/'saved.state') == state_hash
    checks['repair_preserved_package_descriptors'] = all(first[key] == second[key]
        for key in ('roms', 'scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets'))
    cold, rc, text = run('cold-aot', 1600, ['--load', seed/'saved.state'], suffix)
    checks['repaired_cold_aot'] = rc == 0 and 'resource_cache=loaded' in text and 'loaded_state=' in text
    lle, rc, text = run('cold-lle', 1600, ['--load', seed/'saved.state', '--lle'], suffix)
    checks['repaired_cold_lle'] = rc == 0 and 'resource_cache=loaded' in text and 'loaded_state=' in text
    for label, a, b in [('cold_modes', cold, lle), ('warm_cold', warm, cold)]:
        checks[label+'_guest'] = hashes(a/'run.log') == hashes(b/'run.log')
        for name in ('window.png', 'scene.json'):
            checks[label+'_'+name] = digest(a/name) == digest(b/name)
    for name in ('audio.wav', 'attack.csv', 'events.csv'):
        checks['cold_modes_'+name] = digest(cold/name) == digest(lle/name)
    checks['cold_exact_remaining_pcm'] = pcm(cold/'audio.wav') == pcm(warm/'audio.wav')[len(pcm(seed/'audio.wav')):]
    checks['saved_state_still_unchanged'] = digest(seed/'saved.state') == state_hash
    paths = [Path(__file__), build_path, source, ROOT/'scripts/Setup.ps1', ROOT/'dist/LionKing.exe',
             ROOT/'dist/PrepareFinalAssets.exe', original_tape]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  entry_poll_index=tree['poll_index'], actual_setup_run=True, installation_migration_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
