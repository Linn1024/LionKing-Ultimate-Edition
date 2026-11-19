"""Run all native route endpoint pairs through installed-cache Windows playback."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-installed-cache41'
    build_path = base/'build-report.json'
    build = bound(build_path)
    out = base/'native75'
    out.mkdir()
    source = ROOT/'build/pride-porcupine38/complete-wide/report.json'
    template = bound(source)['command']
    cache = base/'verification/Game data & scene cache/scenes-v1.cache'
    assert cache.exists()
    old_path = ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    reference = json.loads(old_path.read_text())
    assert reference['result'] == 'PASS' and reference['route_count'] == 75
    routes = [(p.stem, 5000, p, p.name.endswith('.polled.tape'))
              for p in sorted((ROOT/'engine/build/playtapes').glob('*.tape'))]
    routes += [('idle600', 600, None, False), ('idle3000', 3000, None, False),
               ('idle12000', 12000, None, False),
               ('speedrun1200', 1200, ROOT/'engine/tapes/6987M.read.tape', True),
               ('speedrun6000', 6000, ROOT/'engine/tapes/6987M.read.tape', True)]
    assert len(routes) == 75
    paths = [Path(__file__), build_path, source, cache, old_path]
    paths += [r[2] for r in routes if r[2]]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['SDL_VIDEODRIVER'] = 'dummy'
    assets = []
    for flag in ('--final-menu-assets', '--final-native-assets', '--title-bank-assets'):
        path = Path(template[template.index(flag)+1])
        paths.append(path)
        assets += [flag, str(path)]
    checks = {}
    commands = {}
    results = {}
    def run(route, mode):
        name, frames, tape, polled = route
        folder = out/(name+'-'+mode)
        folder.mkdir()
        config = folder/'host.ini'; config.write_text('opengl = 0\nscale = 1\n')
        profile = folder/'resources.ini'; profile.write_text('schema = 1\ngame = snes\n')
        cmd = [str(base/'player.exe'), '--rom', str(ROOT/'Lion King, The (USA).sfc'),
               '--md-rom', str(ROOT/'Lion King, The (World).md'), '--asset-cache', str(cache),
               '--frames', str(frames), '--config', str(config), '--resource-profile', str(profile),
               '--no-pace', '--no-audio', '--no-record', *assets]
        if tape: cmd += ['--input-polled' if polled else '--input', str(tape)]
        if mode == 'lle': cmd += ['--lle']
        with (folder/'run.log').open('wb') as log:
            process = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=1200, creationflags=subprocess.CREATE_NO_WINDOW)
        text = (folder/'run.log').read_text(errors='replace')
        hashes = dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)', text, re.M))
        return name, mode, hashes, process.returncode, 'resource_cache=loaded' in text, cmd
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run, route, mode) for route in routes for mode in ('aot', 'lle')]
        for future in concurrent.futures.as_completed(futures):
            name, mode, hashes, rc, cached, cmd = future.result()
            results.setdefault(name, {})[mode] = hashes
            commands[name+'-'+mode] = cmd
            checks[name+'-'+mode+'_exit_and_cache'] = rc == 0 and cached and len(hashes) == 2
            if len(results[name]) == 2:
                checks[name+'_mode_parity'] = results[name]['aot'] == results[name]['lle']
                checks[name+'_original_endpoints'] = results[name] == reference['routes'][name]
                print(name, 'MATCH' if checks[name+'_mode_parity'] and checks[name+'_original_endpoints'] else 'FAIL', flush=True)
    checks['all75_routes'] = len(results) == 75
    checks['binary_bound'] = digest(base/'player.exe') == build['binary_sha256']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, routes=results,
                  commands=commands, route_count=75, native_endpoint_only=True,
                  external_reference_sync_or_allbugs_gate_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
