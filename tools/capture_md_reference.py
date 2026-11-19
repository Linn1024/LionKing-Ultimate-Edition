"""Capture a power-on MD movie with its matching portable BizHawk installation.

The emulator/movie are supplied locally; no downloaded input or game data belongs
in git. Use BizHawk 2.11 for ShgofcTAS's https://tasvideos.org/10612S reference.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from md_replay_movie import movie_inputs
from md_lab import ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bizhawk',type=Path,required=True,help='Portable EmuHawk.exe')
    ap.add_argument('--movie',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=ROOT/'build/md-tas/bizhawk')
    ap.add_argument('--frames',type=int,default=6000)
    ap.add_argument('--audio-events',action='store_true',help='Observe original music/FX driver calls in BizHawk')
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    _,header,settings=movie_inputs(args.movie)
    rom=ROOT/'Lion King, The (World).md'
    assert hashlib.md5(rom.read_bytes()).hexdigest().upper() in header.upper(),'Movie ROM differs'
    env=os.environ.copy();env['MD_REFERENCE_OUT']=str(args.out);env['MD_REFERENCE_FRAMES']=str(args.frames)
    if args.audio_events:env['MD_REFERENCE_AUDIO']='1'
    command=[str(args.bizhawk.resolve()),'--config='+str(args.out/'config.ini'),
             '--movie='+str(args.movie.resolve()),'--lua='+str(ROOT/'tools/bizhawk/md_reference.lua'),str(rom)]
    with (args.out/'host.log').open('wb') as stream:
        subprocess.run(command,cwd=args.bizhawk.resolve().parent,env=env,stdout=stream,
                       stderr=subprocess.STDOUT,check=True,timeout=240)
    error=(args.out/'lua-error.txt').read_text();assert not error,error
    with (args.out/'ram.csv').open() as stream:rows=list(csv.DictReader(stream))
    assert rows and int(rows[-1]['frame'])==args.frames,'Reference stopped early'
    transitions=[];previous=None
    for row in rows:
        if row['collision']!=previous:
            transitions.append({'frame':int(row['frame']),'collision':row['collision']});previous=row['collision']
    collisions=[r['collision'] for r in transitions]
    complete='27DA40' in collisions and '1DE09A' in collisions and collisions.index('27DA40')<collisions.index('1DE09A')
    report={'movie':str(args.movie),'movie_sha256':hashlib.sha256(args.movie.read_bytes()).hexdigest(),
            'header':header,'sync_settings':settings,'frames':args.frames,'transitions':transitions,
            'first_level_completed':complete,'full_movie_synchronization_verified':False,
            'music_commands_observed':args.audio_events}
    (args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert complete,'Original MD first-level completion not established'
    print('Original MD first-level reference PASS',json.dumps(transitions),flush=True)


if __name__=='__main__':main()
