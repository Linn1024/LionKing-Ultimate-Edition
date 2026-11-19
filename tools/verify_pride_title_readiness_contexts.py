"""Compare research title input outcomes with ordinary original MD exit routes.

Run with 32-bit Python for the MD reference core. The candidate is LLE-only;
this does not qualify a production player or cold-save implementation.
"""
import csv
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT, MdLab, png
from capture_pride_title_readiness_contexts import picture
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base = ROOT / 'build/pride-title-readiness-probe3'
    candidate = bound(base / 'report.json')
    old = bound(ROOT / 'build/pride-title-upload16/verification/report.json')
    contexts = bound(ROOT / 'build/pride-title-upload16/contexts/report.json')
    fixtures = [ROOT / 'build/pride-game-over-exits-original/prefatal.state',
                ROOT / 'build/pride-final-input-reference/prefatal.state']
    out = base / 'contexts'; out.mkdir()
    checks = {}; observations = {}; commands = {}
    (out / 'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    game = MdLab()
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0,1): game.core.retro_set_controller_port_device(port, 513)
    game.core.retro_unserialize.argtypes = [C.c_void_p,C.c_size_t]; game.core.retro_unserialize.restype = C.c_bool
    game.core.retro_serialize_size.restype = C.c_size_t
    game.core.retro_serialize.argtypes = [C.c_void_p,C.c_size_t]; game.core.retro_serialize.restype = C.c_bool
    pads = ROOT / 'build/pride-final-arena-original/inputs.json'
    fatal = json.loads(pads.read_text())[4597]
    cases = [('go-timeout',True,0,515), ('go-a140',True,256,331), ('go-start140',True,8,331),
             ('continue-no',False,256,331), ('continue-timeout',False,0,1035)]
    try:
        for case, go, dismiss, ready in cases:
            folder = out / case; folder.mkdir()
            raw = fixtures[0 if go else 1].read_bytes(); blob = C.create_string_buffer(raw)
            assert game.core.retro_unserialize(blob,len(raw))
            end = ready + 150
            for age in range(ready-31):
                pad = (fatal if go else 128) if age == 0 else 0
                if dismiss and not go and 130 <= age <= 133: pad = 128
                if dismiss and 140 <= age <= 143: pad = dismiss
                game.step(pad); game.samples.clear()
            n = game.core.retro_serialize_size(); state = C.create_string_buffer(n)
            assert game.core.retro_serialize(state,n)
            (folder / 'original-before-input.state').write_bytes(state.raw)
            plans = [('neutral',0,None,None), ('start',8,ready,ready), ('held',8,ready-20,ready),
                     ('released',8,ready-20,ready-1), ('a',256,ready,ready), ('b',1,ready,ready), ('down',32,ready,ready)]
            original = {}; native = {}; polls = {}
            for label, button, pressed, released in plans:
                assert game.core.retro_unserialize(state,n)
                for age in range(ready-31,end+1):
                    game.step(button if pressed is not None and pressed <= age <= released else 0); game.samples.clear()
                original[label] = picture(game)
                png(folder / f'original-{label}.png',*game.image)
                run_folder = folder / label; run_folder.mkdir()
                if go:
                    template = old['commands']['320-normal700']; origin = 4444
                else:
                    template = contexts['commands']['320-'+('no-live' if dismiss else 'timeout-live')]; origin = 3894
                tape = bytearray(Path(template[template.index('--input')+1]).read_bytes())
                tape.extend(bytes(max(0,(origin+end+2)*2-len(tape))))
                if go and dismiss:
                    for age in range(140,144): struct.pack_into('<H',tape,(origin+age-1)*2,0x1000 if dismiss==8 else 0x8000)
                mapped = {8:0x1000,256:0x8000,1:0x0080,32:0x0400}
                if pressed is not None:
                    for age in range(pressed,released+1): struct.pack_into('<H',tape,(origin+age-1)*2,mapped[button])
                tape_path = run_folder / 'input.tape'; tape_path.write_bytes(tape)
                cmd = template.copy(); cmd[0] = str(base / 'player.exe')
                if '--save-at' in cmd:
                    i = cmd.index('--save-at'); del cmd[i:i+3]
                if '--lle' not in cmd: cmd.append('--lle')
                for flag,value in [('--input',tape_path),('--frames',origin+end),('--config',out/'host.ini'),
                                   ('--dump-window',run_folder/'window.png'),('--dump-scene',run_folder/'scene.json'),('--wav',run_folder/'audio.wav')]:
                    cmd[cmd.index(flag)+1] = str(value)
                env = dict(clean,TLK_FINAL_MD_ART='1',TLK_TITLE_READY_DIR=str(run_folder))
                if not go: env['TLK_CONTINUE_BANK_RECORD'] = str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record')
                with (run_folder/'run.log').open('wb') as log:
                    result = subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
                commands[case+'/'+label] = cmd
                checks[case+'_'+label+'_exit'] = result.returncode==0
                if (run_folder/'window.png').exists(): native[label] = pixels(run_folder/'window.png')
                rows = list(csv.DictReader((run_folder/'actor.csv').open()))
                actual = [int(r['age']) for r in rows if r['pc']=='c4677b']
                polls[label] = min(actual) if actual else None
                checks[case+'_'+label+'_first_poll'] = polls[label]==ready
                print(case,label,'exit',result.returncode,'first poll',polls[label],flush=True)
            original_accepts = {label:value!=original['neutral'] for label,value in original.items()}
            native_accepts = {label:value!=native.get('neutral') for label,value in native.items()}
            for label in original:
                checks[case+'_'+label+'_matches_original'] = label in native and native_accepts[label]==original_accepts[label]
            observations[case] = dict(ready=ready,original_changes=original_accepts,native_changes=native_accepts,first_polls=polls)
    finally:
        game.close()
    paths = [Path(__file__),base/'report.json',ROOT/'tools/capture_pride_title_readiness_contexts.py',pads,*fixtures,
             ROOT/'build/pride-title-upload16/verification/report.json',ROOT/'build/pride-title-upload16/contexts/report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                  research_only=True,original_guest_or_rom_edits=False,binary_sha256=digest(base/'player.exe'),
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__ == '__main__':
    main()
