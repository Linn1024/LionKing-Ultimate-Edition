"""Ordinary power-on flight runs; no guest edits or injected pickups."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--player',default='build/pride-pickup-flight34')
    ap.add_argument('--case',default='256-snes');ap.add_argument('--frames',type=int,default=2000)
    ap.add_argument('--output',default='capture');ap.add_argument('--lle',action='store_true')
    ap.add_argument('--poll-offset',type=int,default=0)
    ap.add_argument('--route',choices=['basic','full'],default='basic');ap.add_argument('--save-at',type=int);ap.add_argument('--load',type=Path)
    ap.add_argument('--art',choices=['snes','md'],default='snes');ap.add_argument('--native-flight',action='store_true');args=ap.parse_args()
    base=ROOT/args.player;bound(base/'build-report.json');out=base/args.output;out.mkdir()
    source=ROOT/'build/pride-restart-difficulty-fixtures/report.json';old=bound(source)
    width,camera=args.case.split('-');profile=out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('md' if width=='320' else 'snes')+
        '\ngameplay.camera = '+camera+'\ngameplay.levels.pride_lands.pickup_flight = '+('snes' if args.native_flight else 'md')+
        '\ngraphics.sprites.pickups = '+args.art+'\n')
    route_source=ROOT/'build/pride-restart-difficulty25/wide-completion/report.json' if width=='320' else ROOT/'build/pride-restart-difficulty25/completion2/report.json'
    if args.route=='full':
        full=bound(route_source);key='aot' if width=='320' else '256-md'
        route_cmd=full['commands'][key]
        profile.write_text(Path(route_cmd[route_cmd.index('--resource-profile')+1]).read_text()+profile.read_text().replace('game = snes\n',''))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    template=old['commands']['md-normal']
    tape=Path(route_cmd[route_cmd.index('--input-polled')+1]) if args.route=='full' else ROOT/'engine/tapes/allbugsF.read.tape'
    original_tape=tape
    if args.poll_offset:
        tape=out/'suffix.polled.tape';tape.write_bytes(original_tape.read_bytes()[args.poll_offset*2:])
    cmd=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--config',config,'--resource-profile',profile,'--input-polled',tape,'--frames',args.frames,'--no-audio','--no-pace','--no-record',
        '--dump-window',out/'window.png','--dump-scene',out/'scene.json','--wav',out/'audio.wav','--wav-seconds',80]))
    for flag in ('--final-menu-assets','--final-native-assets','--title-bank-assets'):cmd +=[flag,template[template.index(flag)+1]]
    if args.lle:cmd.append('--lle')
    if args.save_at:cmd+=['--save-at',str(args.save_at),str(out/'saved.state')]
    if args.load:cmd+=['--load',str((ROOT/args.load).resolve())]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    if args.route=='full':env['TLK_FINAL_MD_ART']='1'
    env.update(TLK_PICKUP_FLIGHT_TRACE=str(out/'flight.csv'),TLK_SOFT_TREE_LOG=str(out/'tree.jsonl'))
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=list(csv.DictReader((out/'flight.csv').open())) if (out/'flight.csv').exists() else []
    checks=dict(exit=run.returncode==0,flight_observed=bool(rows) if not args.native_flight else not rows)
    paths=[Path(__file__),base/'build-report.json',source,original_tape]+([route_source] if args.route=='full' else [])
    if args.load:paths += [(ROOT/args.load).resolve(),(ROOT/args.load).resolve().parent/'report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,
                observations=dict(calls=len(rows),initials=[r for r in rows if r['init']=='1'],arrivals=[r for r in rows if r['arrived']=='1']),
                ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],report['observations'],flush=True)


if __name__=='__main__':main()
