"""Verify bounded natural lizard damage and capture actual Windows hit pictures.

Cross-source hit fields and enemy histories are deliberately retained separately.
This proves neither full enemy AI nor complete difficulty equivalence.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    base = ROOT/'build/pride-difficulty-contact2'
    out = base/'verification'
    out.mkdir(exist_ok=False)
    reports = {s:bound(base/s/'report.json') for s in ('snes', 'md')}
    paths = [Path(__file__), ROOT/'tools/summarize_pride_practice.py',
             *[base/s/'report.json' for s in reports]]
    checks = {}
    observations = {}
    env = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    exe = ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    paths.append(exe)
    for name in ('easy', 'normal', 'hard'):
        native = reports['snes']['cases'][name]
        md = reports['md']['cases'][name]
        for source, case in [('snes', native), ('md', md)]:
            checks[f'{name}_{source}_unit_health_losses'] = [r['before']-r['after'] for r in case['losses']] == [1]*4
        # The native watch labels the executing field zero-based; RAM rows
        # label completed fields one-based. Preserve this explicit conversion.
        first = native['losses'][0]['field']
        watch = re.findall(r'watch \$0B259 ([0-9A-F]{2})->([0-9A-F]{2}).*frame=(\d+)',
                           (base/'snes'/name/'run.log').read_text())
        watch = [(int(a,16), int(b,16), int(f)+1) for a,b,f in watch]
        start = watch.index((0, 100, first))
        countdown = watch[start:start+101]
        checks[name+'_native_100_countdown'] = countdown == [(0,100,first)]+[(v,v-1,first+101-v) for v in range(100,0,-1)]
        rows = json.loads((base/'md'/name/'frames.json').read_text())
        hit = md['losses'][0]['field']
        selected = [r for r in rows if hit <= r['field'] <= hit+100]
        checks[name+'_md_100_countdown'] = [r['immunity'] for r in selected] == list(range(100,-1,-1))
        checks[name+'_md_protected_health'] = all(r['health']==3 for r in selected)
        observations[name] = dict(snes_first_hit=first, md_first_hit=hit,
            snes_loss_offsets=[r['field']-native['initial']['field'] for r in native['losses']],
            md_loss_offsets=[r['field']-md['initial']['field'] for r in md['losses']])
        folder = out/name
        folder.mkdir()
        cfg = folder/'host.ini'
        cfg.write_text('opengl = 0\nscale = 2\n')
        cmd = [exe, '--rom', ROOT/'Lion King, The (USA).sfc', '--resource-profile', base/'snes'/name/'resources.ini',
               '--config', cfg, '--input', base/'snes'/name/'ordinary.tape', '--frames', first,
               '--no-pace', '--no-audio', '--no-record', '--dump-scene', folder/'scene.json',
               '--dump-window', folder/'window.png', '--dump-png', folder/'guest.png']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=90)
        guest = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        checks[name+'_real_player_hit_state'] = (guest['health']==3 and
            guest['player']==[native['losses'][0]['x'],native['losses'][0]['y']])
    for source in ('snes', 'md'):
        offsets = [observations[n][source+'_loss_offsets'] for n in observations]
        checks[source+'_difficulty_loss_offsets'] = offsets[0] == offsets[1] == offsets[2]
    assert all(checks.values()), checks
    result = dict(result='BOUNDED_CONTACT_RESOURCES_MATCH', scope=__doc__, checks=checks,
        observations=observations, contact_time_equivalence_claimed=False,
        full_difficulty_or_enemy_equivalence=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['result'], len(checks), 'checks', flush=True)


if __name__ == '__main__':
    main()
