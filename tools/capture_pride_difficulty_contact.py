"""Observe ordinary first-level health losses after the verified difficulty boots.

SNES walks right for 95 fields before neutral input; MD retains its verified
boot prefix ending farther right. Contact times
between sources are not equated. No guest writes, practice mode or state loads.
"""
import argparse
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT, MdLab, png
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', choices=('snes', 'md'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--native-approach', type=int, default=95)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    base = ROOT/'build/pride-difficulty-start2'/args.source
    report_path = base/'report.json'
    bound(report_path)
    paths = [Path(__file__), ROOT/'tools/md_lab.py', report_path]
    cases = {}
    env = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    for name in ('easy', 'normal', 'hard'):
        folder = out/name
        folder.mkdir()
        rows = []
        if args.source == 'md':
            game = MdLab()
            game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
            for port in (0, 1):
                game.core.retro_set_controller_port_device(port, 513)
            prefix = json.loads((base/name/'inputs.json').read_text())
            previous = 4
            try:
                for field, pad in enumerate(prefix+[0]*2400, 1):
                    game.step(pad)
                    game.samples.clear()
                    if field < len(prefix):
                        continue
                    word = lambda a: game.work_ram[a] | game.work_ram[a+1] << 8
                    camera = word(0xcd36)
                    player = word(camera+0x24) if camera <= 0xffda else 0
                    valid = 0x8000 <= player <= 0xff80
                    row = dict(field=field, health=word(0xccf6), lives=word(0xccee),
                               level=word(0xccce), player=player,
                               x=word(player+8) if valid else None,
                               y=word(player+10) if valid else None,
                               immunity=word(player+0x46) if valid else None,
                               action=(word(player+0x30)<<16 | word(player+0x32)) if valid else None)
                    rows.append(row)
                    if row['health'] < previous and word(0xccce) == 1:
                        png(folder/f'hit-{field}.png', *game.image)
                        (folder/f'hit-{field}-wram.bin').write_bytes(bytes(game.work_ram))
                    previous = row['health']
            finally:
                game.close()
        else:
            exe = ROOT/'engine/build-win/tlk_headless.exe'
            prefix = (base/name/'ordinary.tape').read_bytes()
            start = len(prefix)//2
            tape = folder/'ordinary.tape'
            tape.write_bytes(prefix+struct.pack('<'+'H'*2400,
                *([0x100]*args.native_approach+[0]*(2400-args.native_approach))))
            profile = folder/'resources.ini'
            profile.write_text('schema = 1\ngame = snes\n')
            cmd = [exe, '--rom', ROOT/'Lion King, The (USA).sfc',
                   '--resource-profile', profile, '--input', tape, '--frames', str(start+2400),
                   '--ram-log', folder/'ram.log']
            watch_env = dict(env, TLK_WATCH='0xb259')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str, cmd)), cwd=ROOT, env=watch_env, stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=180)
            for line in (folder/'ram.log').read_text().splitlines():
                parts = line.split()
                field = int(parts[0])
                if field < start:
                    continue
                rows.append(dict(field=field, health=int(parts[3], 16),
                                 x=int(parts[4], 16), y=int(parts[5], 16),
                                 level=int(parts[6], 16), lives=int(parts[7], 16)))
        losses = [dict(field=b['field'], before=a['health'], after=b['health'],
                       x=b['x'], y=b['y']) for a,b in zip(rows, rows[1:])
                  if b['health'] < a['health'] and b['level'] == (1 if args.source == 'md' else 0)]
        cases[name] = dict(initial=rows[0], losses=losses, final=rows[-1])
        (folder/'frames.json').write_text(json.dumps(rows, indent=2)+'\n')
        print(args.source, name, losses, flush=True)
    paths += ([ROOT/'engine/build-win/tlk_headless.exe', ROOT/'Lion King, The (USA).sfc']
              if args.source == 'snes' else [ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
                                            ROOT/'Lion King, The (World).md'])
    result = dict(result='CAPTURED', scope=__doc__, source=args.source,
                  native_approach_fields=args.native_approach if args.source=='snes' else None,
                  cases=cases, source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix():digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
