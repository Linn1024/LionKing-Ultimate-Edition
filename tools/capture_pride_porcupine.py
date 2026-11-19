"""Ordinary Windows attack capture, with explicit source/mode/save selection."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--player',default='build/pride-porcupine36')
    ap.add_argument('--output',required=True);ap.add_argument('--frames',type=int,default=1530)
    ap.add_argument('--source',choices=['snes','md'],default='md');ap.add_argument('--lle',action='store_true')
    ap.add_argument('--save-at',type=int);ap.add_argument('--load',type=Path);ap.add_argument('--poll-offset',type=int,default=0)
    ap.add_argument('--profile',type=Path);ap.add_argument('--tape',type=Path,default=Path('engine/tapes/allbugsF.read.tape'))
    args=ap.parse_args();base=ROOT/args.player;bound(base/'build-report.json')
    out=base/args.output;out.mkdir()
    template_path=ROOT/'build/pride-pickup-flight35/wide-warm/report.json'
    template=bound(template_path)['command'];cmd=template.copy();cmd[0]=str(base/'player.exe')
    profile=out/'resources.ini';profile.write_text((ROOT/args.profile).read_text() if args.profile else 'schema = 1\ngame = snes\n')
    with profile.open('a') as stream:stream.write('\ngameplay.levels.pride_lands.porcupine_attack = '+args.source+'\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    original_tape=ROOT/args.tape;tape=original_tape
    if args.poll_offset:
        tape=out/'suffix.polled.tape';tape.write_bytes(original_tape.read_bytes()[args.poll_offset*2:])
    for flag,value in [('--config',config),('--resource-profile',profile),('--input-polled',tape),('--frames',args.frames),
                       ('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json'),('--wav',out/'audio.wav')]:
        cmd[cmd.index(flag)+1]=str(value)
    if args.lle:cmd.append('--lle')
    if args.save_at:cmd+=['--save-at',str(args.save_at),str(out/'saved.state')]
    if args.load:cmd+=['--load',str(ROOT/args.load)]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(TLK_PORCUPINE_ATTACK_TRACE=str(out/'attack.csv'),TLK_AUDIO_EVENTS=str(out/'events.csv'),
               TLK_MD_SOUND_COMMANDS=str(out/'driver.csv'),TLK_SOFT_TREE_LOG=str(out/'tree.jsonl'))
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=list(csv.DictReader((out/'attack.csv').open())) if (out/'attack.csv').exists() else []
    events=list(csv.DictReader((out/'events.csv').open())) if (out/'events.csv').exists() else []
    cues=[r for r in rows if r['pc']=='c15cb2' and r['phase_before']=='3']
    checks=dict(exit=run.returncode==0,source_observed=bool(rows) if args.source=='md' else not rows,
                late_cue=all(r['timer']=='28' for r in cues))
    paths=[Path(__file__),base/'build-report.json',template_path,original_tape]
    if args.profile:paths.append(ROOT/args.profile)
    if args.load:paths.append(ROOT/args.load)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,
                observations=dict(boundaries=len(rows),cues=cues,events=events),
                ordinary_controller_inputs=True,guest_rom_or_rng_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(rows),'boundaries',len(cues),'cues',flush=True)


if __name__=='__main__':main()
