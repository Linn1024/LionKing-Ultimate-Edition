"""Isolate native stop-packet timing, intentionally allowing dual music."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-music-transport59'
    bp = base/'build-report.json'; build = bound(bp)
    source = ROOT/'build/pride-hyena-mixtures58/report.json'; prior = bound(source)
    out = base/'verification'; out.mkdir(); checks = {}; commands = {}; observations = {}
    clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    clean['SDL_VIDEODRIVER'] = 'dummy'
    def run(item):
        name, music, mode, public = item; folder = out/name; folder.mkdir()
        cmd = prior['commands']['hard-art-aot'].copy()
        cmd[0] = str(ROOT/'dist/installed-preview53/LionKing.exe' if public else base/'player.exe')
        cmd[cmd.index('--hash-at')+1] = ','.join(map(str, range(1,4601)))
        profile = Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        if music: profile += 'audio.music.pride_lands = md\n'
        (folder/'resources.ini').write_text(profile)
        (folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag, file in [('--config','host.ini'), ('--resource-profile','resources.ini'),
                           ('--dump-window','window.png'), ('--dump-scene','scene.json'), ('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/file)
        if mode == 'lle': cmd += ['--lle']
        commands[name] = cmd
        env = dict(clean, TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'), TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:
            rc = subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene = json.loads((folder/'scene.json').read_text())
        owned = [p for p in scene['pieces'] if p['actor_descriptor']==0xc58c68 and
                 p['actor_owner']==p['object'] and p['actor_action']==0xc147f7]
        checks[name+'_exit'] = rc == 0
        checks[name+'_owned_dead_boss'] = bool(owned)
        checks[name+'_player_alive'] = scene['latched_gameplay']['health'] > 0
        rows = list(csv.DictReader((folder/'driver.csv').open())) if (folder/'driver.csv').exists() else []
        tracks = sorted({int(r['value']) for r in rows if r['selector']=='1'})
        checks[name+'_music_choice_observed'] = ({134,137} <= set(tracks)) if music else not tracks
        observations[name] = dict(health=scene['latched_gameplay']['health'],death_pieces=len(owned),md_tracks=tracks)
        print(name,rc,observations[name],flush=True)
        return name, folder
    cases = [('public-native',False,'aot',True)] + [
        (f'{choice}-{mode}',choice=='music',mode,False)
        for choice in ('native','music') for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool: runs = dict(pool.map(run,cases))
    pattern = r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    reference = hashes(runs['public-native'])
    checks['reference_all4600_fields'] = len(reference) == 4600
    for name, folder in runs.items():
        if name=='public-native':continue
        checks[name+'_all4600_guest_picture_full_wram_equal_native'] = hashes(folder) == reference
        checks[name+'_canonical_scene_equal_native'] = digest(folder/'scene.json') == digest(runs['public-native']/'scene.json')
        if name.startswith('native'):
            checks[name+'_whole_native_pcm_preserved'] = digest(folder/'audio.wav') == digest(runs['public-native']/'audio.wav')
        else:
            checks[name+'_md_audio_present'] = digest(folder/'audio.wav') != digest(runs['public-native']/'audio.wav')
    checks['music_whole_pcm_mode_parity'] = digest(runs['music-aot']/'audio.wav') == digest(runs['music-lle']/'audio.wav')
    checks['binary_exact'] = digest(base/'player.exe') == build['binary_sha256']
    paths = [Path(__file__),bp,source]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                  causal_transport_experiment=True,dual_music_intentional=True,production_audio_fix=False,
                  public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
