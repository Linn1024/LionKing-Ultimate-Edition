"""Qualify strict installed scene-cache loading in actual Windows playback."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    out = ROOT/'build/pride-installed-cache41/verification'
    out.mkdir()
    build_path = out.parent/'build-report.json'
    build = bound(build_path)
    old_build_path = ROOT/'build/pride-porcupine38/build-report.json'
    old_build = bound(old_build_path)
    source = ROOT/'build/pride-porcupine38/complete-wide/report.json'
    template = bound(source)['command']
    checks = {}
    commands = {}
    paths = [Path(__file__), build_path, old_build_path, source]
    cache = out/'Game data & scene cache/scenes-v1.cache'
    cache.parent.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    def run(label, extra=(), old=False, frames=1, cached=None, debugger=None, full_hashes=False):
        folder = out/label
        folder.mkdir()
        cmd = template.copy()
        cmd[0] = str(ROOT/'build/pride-porcupine38/player.exe' if old else out.parent/'player.exe')
        for flag, value in [('--frames', frames), ('--wav-seconds', 140),
                            ('--dump-window', folder/'window.png'), ('--dump-scene', folder/'scene.json'),
                            ('--wav', folder/'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        for flag, name in [('--config', 'host.ini'), ('--resource-profile', 'resources.ini')]:
            file = folder/name
            file.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
            cmd[cmd.index(flag)+1] = str(file)
        protected = {name: digest(folder/name) for name in ('host.ini', 'resources.ini')}
        if cached is not None: cmd += ['--asset-cache', str(cached)]
        if full_hashes: cmd += ['--hash-at', ','.join(map(str, range(1, frames+1)))]
        cmd += list(map(str, extra))
        if debugger: cmd = ['C:/mingw32/bin/gdb.exe', '--batch', '-x', str(debugger), '--args', *cmd]
        assert len(subprocess.list2cmdline(cmd)) < 32760
        commands[label] = cmd
        child = env.copy()
        child.update(TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                     TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'), TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            result = subprocess.run(cmd, cwd=ROOT, env=child, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=240, creationflags=subprocess.CREATE_NO_WINDOW)
        text = (folder/'run.log').read_text(errors='replace')
        checks[label+'_settings_preserved'] = all(digest(folder/name) == sha for name, sha in protected.items())
        print(label, result.returncode, flush=True)
        return folder, result.returncode, text
    prep, rc, text = run('prepare', extra=['--prepare-resources', cache])
    checks['preparation_succeeds'] = rc == 0 and 'resource_cache=prepared' in text and cache.exists()
    checks['preparation_exits_before_guest'] = not (prep/'window.png').exists() and 'frame_sha256=' not in text
    blob = cache.read_bytes()
    original_digest = digest(cache)
    cases = dict(missing=cache.parent/'missing.cache', empty='', directory=cache.parent)
    damaged = {}
    damaged['short_header'] = blob[:50]
    data = bytearray(blob); struct.pack_into('<I', data, 8, 0); damaged['wrong_version'] = data
    data = bytearray(blob); data[16] ^= 1; damaged['wrong_snes_hash'] = data
    data = bytearray(blob); data[48] ^= 1; damaged['wrong_md_hash'] = data
    data = bytearray(blob); data[-1] ^= 1; damaged['bad_payload_digest'] = data
    damaged['truncated'] = blob[:-1]
    damaged['trailing_byte'] = blob+b'\x00'
    data = bytearray(blob); data[112] ^= 1; data[80:112] = hashlib.sha256(data[112:]).digest()
    damaged['invalid_structure_valid_digest'] = data
    for label, data in damaged.items():
        path = cache.parent/(label+'.cache')
        path.write_bytes(data)
        cases[label] = path
    for label, path in cases.items():
        folder, rc, text = run('reject-'+label, cached=path)
        checks[label+'_stops_before_guest'] = (rc == 8 and 'Cannot load installed game data:' in text
            and 'frame_sha256=' not in text and not (folder/'window.png').exists()
            and not (folder/'audio.wav').exists() and 'miss_decoded_from_rom' not in text)
        checks[label+'_preserves_good_cache'] = digest(cache) == original_digest
    failed, rc, text = run('prepare-failure', extra=['--prepare-resources', cache.parent/'absent/scene.cache'])
    checks['failed_preparation_preserves_installation'] = (rc == 8 and digest(cache) == original_digest
        and not (failed/'window.png').exists())
    # Observe actual function entries, without changing guest memory or registers.
    script = out/'cache-calls.gdb'
    script.write_text('''set pagination off
set confirm off
break TlkMdAssetsInit
commands
silent
printf "SCENE_DECODE_CALLED\\n"
continue
end
break TlkMdAssetsBindSnes
commands
silent
printf "SCENE_BIND_CALLED\\n"
continue
end
break TlkMdSpritesInit
commands
silent
printf "OTHER_RESOURCE_PREP_CALLED\\n"
continue
end
break SnesInit
commands
silent
printf "GUEST_INIT_CALLED\\n"
continue
end
run
''')
    paths.append(script)
    folder, rc, text = run('missing-debugger', cached=cases['missing'], debugger=script)
    checks['missing_never_calls_decoder_other_preparation_or_guest'] = (rc == 0
        and 'exited with code 010' in text and not any(marker in text for marker in
        ('SCENE_DECODE_CALLED', 'SCENE_BIND_CALLED', 'OTHER_RESOURCE_PREP_CALLED', 'GUEST_INIT_CALLED')))
    normal, rc, text = run('valid-one', cached=cache)
    checks['valid_cache_loads'] = rc == 0 and 'resource_cache=loaded' in text
    debug, rc, text = run('valid-debugger', cached=cache, debugger=script)
    checks['valid_never_calls_scene_decoder'] = (rc == 0 and 'SCENE_DECODE_CALLED' not in text
        and 'SCENE_BIND_CALLED' not in text and 'GUEST_INIT_CALLED' in text)
    checks['other_startup_asset_migration_still_needed'] = 'OTHER_RESOURCE_PREP_CALLED' in text
    checks['debugger_guest_neutral'] = hashes(normal/'run.log') == hashes(debug/'run.log')
    for name in ('window.png', 'scene.json', 'audio.wav'):
        checks['debugger_'+name+'_neutral'] = digest(normal/name) == digest(debug/name)
    outputs = {}
    for label, old, extra in [('full-reference', True, []), ('full-aot', False, []), ('full-lle', False, ['--lle'])]:
        folder, rc, text = run(label, old=old, extra=extra, frames=6000, cached=cache, full_hashes=True)
        outputs[label] = folder
        checks[label+'_exit_and_cache'] = rc == 0 and 'resource_cache=loaded' in text
        rows = re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)', text)
        checks[label+'_all_6000_guest_fields'] = len(rows) == 6000
        tree = json.loads((folder/'tree.jsonl').read_text().splitlines()[-1])
        checks[label+'_reaches_next_level'] = tree['level'] == 1 and tree['lives'] == 8
    for label, before, after in [('modes', 'full-aot', 'full-lle'), ('prior_preserved', 'full-reference', 'full-aot')]:
        a = outputs[before]; b = outputs[after]
        all_hashes = lambda p: re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)', p.read_text())
        checks[label+'_every_guest_field'] = all_hashes(a/'run.log') == all_hashes(b/'run.log')
        checks[label+'_final_guest'] = hashes(a/'run.log') == hashes(b/'run.log')
        for name in ('window.png', 'scene.json', 'audio.wav', 'attack.csv', 'events.csv'):
            checks[label+'_'+name] = digest(a/name) == digest(b/name)
    checks['route_pcm_covers_over_90_seconds'] = len(pcm(outputs['full-aot']/'audio.wav')) > 90*48000*4
    checks['only_two_of_321_inputs_changed'] = len(build['link_inputs_sha256']) == 321 and build['unchanged_link_inputs'] == 319
    checks['candidate_binary_bound'] = digest(out.parent/'player.exe') == build['binary_sha256']
    checks['prior_binary_unchanged'] = digest(old_build_path.parent/'player.exe') == old_build['binary_sha256']
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT/'engine').strip()
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  explicit_installed_scene_cache_only=True, whole_installation_migration_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
