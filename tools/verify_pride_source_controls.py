"""Compare actual source restarts to cold boots fed the original level macro."""
import argparse
import json
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment


def macro_tape(original):
    # Same ordinary debug-menu inputs as BuildLevelMacro(level0,invul0), with
    # no guest writes. Feed them from field0 after loading the actual boot save;
    # --practice-level would first consume a discarded field/audio interval.
    words=[]
    def wait(n):words.extend([0]*n)
    def tap(value):words.extend([value]*2);wait(4)
    wait(700);tap(1<<5);wait(10);tap(1<<3);wait(80)
    for value,delay in ((1,20),(1<<8,20),(1<<11,20),(1<<11,20),(1<<1,60)):
        tap(value);wait(delay)
    tap(1<<5);wait(20);wait(20);tap(1<<3);wait(60);tap(1<<4);wait(20);tap(1<<3)
    assert len(words)==1116
    tail=list(struct.unpack('<'+'H'*(len(original)//2),original))
    # joypad_auto_read_word reverses16 bits; RtlRunFrame uses low12 host bits.
    convert=lambda word:int(f'{word:016b}'[::-1],2)&0xfff
    return struct.pack('<'+'H'*3000,*(words+[convert(w) for w in tail[len(words):3000]]))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--case',choices=('snes','md'),required=True);args=p.parse_args()
    root=ROOT/args.root;r_path=root/'report.json';r=bound(r_path);assert r['result']=='PASS'
    out=root/'controls'/args.case;out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists()
    command=list(r['command']);binary=Path(command[0]);assert digest(binary)==r['binary_sha256']
    dll=binary.parent/'genesis_plus_gx_libretro.dll';assert digest(dll)==r['dll_sha256']
    profile=root/(args.case+'.ini');boot=root/'boot-author/tlk_practice_boot.state'
    original=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';tape=out/'level-select.raw';tape.write_bytes(macro_tape(original.read_bytes()))
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    command[command.index('--config')+1]=str(config);command[command.index('--resource-profile')+1]=str(profile)
    command[command.index('--input')]='--input-raw';command[command.index('--input-raw')+1]=str(tape)
    for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
        command[command.index(flag)+1]=str(out/name)
    command+=['--load',str(boot),'--no-pace']
    env=environment(out);env['TLK_MD_SOUND_COMMANDS']=str(out/'md-commands.csv');env['TLK_AUDIO_STEMS']=str(out/'audio-stems.csv')
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    checks=dict(exit=result.returncode==0,profile_loaded='Saved resource profile loaded' in (out/'run.log').read_text(),
        automatic_restart=(out/'tlk_practice_restart.state').exists())
    state=(out/'tlk_practice_restart.state').read_bytes()
    checks['actual_cold_restart_snapshot']=state==(root/f'automatic-{args.case}.state').read_bytes()
    paths=(Path(__file__),r_path,profile,boot,original,ROOT/'engine/runner/sdl_main.c',ROOT/'engine/snesrecomp/runner/src/snes/joypad.c',ROOT/'tools/verify_pride_live_error_ui.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,binary_sha256=digest(binary),dll_sha256=digest(dll),command=command,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
