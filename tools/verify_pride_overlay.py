"""Real F5 notification blending against mixed clients, before/during revival."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment, read_rows, toast_image
from verify_windows import USER32, window_for, hashes, pixels


def mixed_toast(reference, message):
    """Independent RGB oracle: tint the actual final client, then stamp font."""
    width, height, base = pixels(reference)
    assert (width, height) in ((512, 448), (640, 448))
    font = (ROOT/'engine/runner/tlk_font8x8.h').read_text()
    glyphs = [[int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]+)', row)]
              for row in re.findall(r'\{([^{}]+)\}', font)]
    assert len(glyphs) == 95 and all(len(g) == 8 for g in glyphs)
    lines = []
    text = message
    while text and len(lines) < 9:
        text = text.lstrip(' ')
        if not text: break
        length = len(text.split('\n', 1)[0]); take = min(length, 30)
        if length > 30:
            split = take
            while split and text[split] != ' ': split -= 1
            if split: take = split
        lines.append(text[:take]); text = text[take:]
        if text.startswith('\n'): text = text[1:]
    extra = (width//2 - 256)//2
    for y in range(4, 4 + len(lines)*10 + 6):
        for x in range(4, 4 + max(map(len, lines))*8 + 8):
            white = False
            if y >= 8:
                line, row = divmod(y-8, 10)
                if line < len(lines) and row < 8 and 8 <= x < 8+len(lines[line])*8:
                    char = lines[line][(x-8)//8]
                    white = bool(glyphs[ord(char)-32][row] & (1 << ((x-8)%8)))
            for dy in (0, 1):
                for dx in (0, 1):
                    i = (y*2+dy)*width+(extra+x)*2+dx
                    base[i] = (255,255,255) if white else tuple(c*25//255 for c in base[i])
    return width, height, base


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', choices=('md-owned','native-owned','md-ordinary','native-ordinary'), required=True)
    p.add_argument('--software', action='store_true')
    args = p.parse_args(); md = args.case.startswith('md'); owned = args.case.endswith('owned')
    base = ROOT/'build/pride-overlay'; out = base/'windows'/(args.case+('-software' if args.software else ''))
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'report.json').exists(), 'Use a fresh capture directory'
    build_path = base/'build-report.json'; build = json.loads(build_path.read_text()); binary = base/'overlay-sdl.exe'
    for name, sha in build['source_sha256'].items(): assert digest(ROOT/name) == sha, name
    assert digest(binary) == build['runs']['sdl']['binary_sha256']
    old = ROOT/'build/pride-practice/verified/normal-ui'/('md-lle' if md else 'native-aot')
    profile = out/'resources.ini'; profile.write_bytes((old/'resources.ini').read_bytes())
    tape = ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'; commands = {}
    def command(name, end):
        folder = out/name; folder.mkdir(exist_ok=True)
        config = folder/'host.ini'; config.write_text(f'opengl = {int(not args.software)}\nscale = 2\n')
        cmd = [binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
               '--resource-profile',profile,'--config',config,'--input',tape,'--frames',end,
               '--no-audio','--no-record','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
               '--wav',folder/'audio.wav','--wav-seconds',100]
        if md: cmd += ['--lle']
        return folder, list(map(str, cmd))
    def run(cmd, folder):
        with (folder/'run.log').open('wb') as log:
            r = subprocess.run(cmd,cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=150)
        assert r.returncode == 0, (folder, r.returncode)
    author, cmd = command('author',1300)
    cmd += ['--no-pace','--speedrun','practice']; commands['author'] = cmd; run(cmd,author)
    state = author/'tlk_practice_restart.state'; raw = bytearray(state.read_bytes())
    assert raw[:8] == b'PRPRAC01'
    raw[56] ^= 1
    end = 2100 if owned else 1600; target = (2042 if md else 2041) if owned else 1550
    control, cmd = command('control',end); cmd += ['--load',str(state),'--no-pace']; commands['control'] = cmd; run(cmd,control)
    candidate, cmd = command('candidate',end); cmd += ['--load',str(state)]; commands['candidate'] = cmd
    (candidate/'tlk_slot1.state').write_bytes(raw)
    USER32.SetProcessDPIAware(); hwnd = None; until = time.monotonic()+90
    with (candidate/'run.log').open('wb') as log:
        proc = subprocess.Popen(cmd,cwd=ROOT,env=environment(candidate),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while not hwnd:
                hwnd=window_for(proc.pid); assert proc.poll() is None and time.monotonic()<until; time.sleep(.005)
            while True:
                rows=read_rows(candidate/'practice-fields.csv')
                if rows and int(rows[-1]['field'])>=target: break
                assert proc.poll() is None and time.monotonic()<until; time.sleep(.003)
            assert USER32.PostMessageW(hwnd,0x100,116,1); assert USER32.PostMessageW(hwnd,0x101,116,0xc0000001)
            code=proc.wait(timeout=90)
        finally:
            if proc.poll() is None:
                USER32.PostMessageW(hwnd,0x10,0,0)
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.terminate(); proc.wait(timeout=5)
    loads=read_rows(candidate/'live-load.csv'); failed=[r for r in loads if r['success']=='0']
    message='Slot 1: Ordinary-play save is incompatible or damaged'
    actual=pixels(candidate/'window.png'); expected=mixed_toast(control/'window.png',message)
    legacy=toast_image(control/'window.png',control/'guest.png',message)
    checks=dict(exit=code==0,actual_f5=len(loads)==2 and len(failed)==1,
        correct_attempt_field=len(failed)==1 and target<=int(failed[0]['attempt_field'])<=target+9,
        guest=hashes(candidate/'run.log')==hashes(control/'run.log'),
        native_image=pixels(candidate/'guest.png')==pixels(control/'guest.png'),
        pcm=wav_data(candidate/'audio.wav')==wav_data(control/'audio.wav'),
        mixed_client=actual==expected,slot_preserved=(candidate/'tlk_slot1.state').read_bytes()==raw,
        error_text=message in (candidate/'run.log').read_text())
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
        checks[name]=read_rows(candidate/name)==read_rows(control/name)
    if owned:
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv'):
            checks[name]=digest(candidate/'restart-1'/name)==digest(control/'restart-1'/name)
    legacy_differences=sum(a!=b for a,b in zip(expected[2],legacy[2]))
    if md: checks['legacy_native_imprint_removed']=legacy_differences>0 and actual!=legacy
    paths=(Path(__file__),build_path,profile,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'engine/runner/tlk_font8x8.h')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,software=args.software,
        loads=loads,pixels_compared=actual[0]*actual[1],legacy_difference_pixels=legacy_differences,
        binary_sha256=digest(binary),source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},commands=commands,
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.case,'software' if args.software else 'GL',report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()): raise SystemExit(1)


if __name__=='__main__': main()
