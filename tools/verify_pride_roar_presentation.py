"""Compare first loaded roar fields, including pause, with either artwork source."""
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels


def main():
    out = ROOT/'build/pride-roar-presentation'
    out.mkdir(parents=True, exist_ok=True)
    ready = ROOT/'build/pride-roar-behavior/snes-ready.state'
    tape = ROOT/'build/pride-roar-behavior/input.tape'
    assert ready.is_file() and tape.is_file(), 'Run verify_pride_roar_behavior.py first'
    paused = bytearray(tape.read_bytes())
    for frame in (2490, 2510):
        pad = struct.unpack_from('<H', paused, frame*2)[0]
        struct.pack_into('<H', paused, frame*2, pad | 0x1000)
    pause_tape = out/'pause.tape'
    pause_tape.write_bytes(paused)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    base = [str(ROOT/'dist/LionKing.exe'), '--rom', str(ROOT/'Lion King, The (USA).sfc'),
            '--md-rom', str(ROOT/'Lion King, The (World).md'), '--config', str(config),
            '--no-pace', '--no-audio', '--no-record']
    results = []
    for art in ('snes', 'md'):
        profile = out/(art+'.ini')
        choices = 'schema = 1\ngame = snes\n'
        if art == 'md':
            choices = '\n'.join(line for line in (ROOT/'profiles/pride-lands.ini').read_text().splitlines()
                                if not line.startswith(('audio.', 'gameplay.'))) + '\n'
        profile.write_text(choices+'gameplay.simba.roar = md\n')

        def run(name, frame, source_state, input_path, save=None, capture=True):
            logpath = out/(name+'.log')
            command = [*base, '--resource-profile', str(profile), '--load', str(source_state),
                       '--frames', str(frame), '--input', str(input_path)]
            if save:
                command += ['--save-at', str(frame), str(save)]
            if capture:
                command += ['--dump-window', str(out/(name+'.png')), '--dump-scene', str(out/(name+'.json'))]
            with logpath.open('wb') as log:
                subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=120)
            return hashes(logpath)

        for frame in (2487, 2488, 2528, 2493):
            name = f'{art}-{frame}'
            active_tape = pause_tape if frame == 2493 else tape
            reference = run(name+'-continuous', frame+1, ready, active_tape)
            state = out/(name+'.state')
            run(name+'-save', frame, ready, active_tape, state, False)
            assert struct.unpack_from('<I', state.read_bytes(), 32)[0] & 16
            resumed = run(name+'-loaded', frame+1, state, active_tape)
            assert resumed == reference, (name, 'guest hashes')
            assert json.loads((out/(name+'-loaded.json')).read_text()) == json.loads((out/(name+'-continuous.json')).read_text()), (name, 'scene history')
            assert pixels(out/(name+'-loaded.png')) == pixels(out/(name+'-continuous.png')), (name, 'first field')
            if frame == 2493:
                env = os.environ.copy()
                env.update(TLK_WRAM_DUMP=str(frame+1), TLK_WRAM_DIR=str(out))
                with (out/(name+'-pause-check.log')).open('wb') as log:
                    subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'), '--rom',
                                    str(ROOT/'Lion King, The (USA).sfc'), '--md-rom',
                                    str(ROOT/'Lion King, The (World).md'), '--resource-profile', str(profile),
                                    '--load', str(state), '--frames', str(frame+1), '--input', str(active_tape)],
                                   cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
                ram = (out/f'hl_wram_{frame+1}.bin').read_bytes()
                word = lambda address: struct.unpack_from('<H', ram, address)[0]
                assert word(0xa89) and word(0xb243) == 0x589c, 'Fixture must pause during the roar'
                # Resume through the ordinary second Start press as well.
                assert run(name+'-unpause-reference', 2584, ready, active_tape, capture=False) == run(name+'-unpause-loaded', 2584, state, active_tape, capture=False)
            results.append(name)
            print(name, 'first loaded window/scene/guest state identical PASS', flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS', 'scope':__doc__,
        'identical_first_fields':results, 'paused_mid_roar':True, 'ordinary_unpause_continuation':True}, indent=2)+'\n')


if __name__ == '__main__':
    main()
