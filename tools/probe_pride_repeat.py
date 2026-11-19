"""Capture two ordinary nonfinal revivals with independently selected resources."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes

BASE=ROOT/'build/pride-repeat'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',choices=('snes','md'),default='snes');p.add_argument('--width',type=int,choices=(256,320),default=256)
    p.add_argument('--graphics',choices=('native','frames','palette','all'),default='native');p.add_argument('--mode',choices=('aot','lle'),default='aot')
    p.add_argument('--sdl',action='store_true');p.add_argument('--frames',type=int,default=3000)
    p.add_argument('--save-at',type=int)
    p.add_argument('--output-root',type=Path,default=BASE/'first');args=p.parse_args()
    out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True);host='sdl' if args.sdl else 'probe'
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text());binary=BASE/f'repeat-{host}.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs'][host]['binary_sha256']
    reference=ROOT/'build/pride-actor-handoff/active'/f'{args.start}-default-{args.width}-{args.graphics}-{args.mode}-owned'
    profile=out/'resources.ini';profile.write_bytes((reference/'resources.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--input',tape,'--frames',args.frames]
    if args.mode=='lle':command+=['--lle']
    if args.save_at:command+=['--save-at',args.save_at,out/'second.private-state']
    if args.sdl:
        config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        command+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',out/'window.png',
            '--dump-png',out/'guest.png','--wav',out/'audio.wav','--wav-seconds','100']
    else:command+=['--ram-log',out/'route.ram','--wide',args.width,'--wide-png',out/'picture.png']
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(list(map(str,command)),cwd=ROOT,env=environment(out),stdout=log,stderr=subprocess.STDOUT,timeout=240)
    events=read_rows(out/'owner-events.csv');begins=[e for e in events if e['event']=='begin'];normal=[e for e in events if e['event']=='normal']
    checks=dict(exit=run.returncode==0,two_begins=len(begins)==2,two_normals=len(normal)==2)
    folders=[out]+sorted(p for p in out.glob('scene-*') if p.is_dir())
    scenes=[]
    for folder in folders:
        records=read_rows(folder/'render-fields.csv')
        scenes.append(dict(folder=folder.name,begin_field=int(records[0]['field']),release_field=int(records[-1]['field']),
            release_age=int(records[-1]['age']),released=records[-1]['released']=='1',mismatch=int(records[-1]['native_pixel_mismatch'])))
    checks['two_render_releases']=len(scenes)==2 and all(s['released'] and not s['mismatch'] and 300<=s['release_age']<=308 for s in scenes)
    checks['normal300']=len(normal)==2 and all(e['age']=='300' for e in normal)
    source={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),build_path,reference/'resources.ini',tape,ROOT/'tools/verify_pride_live_error_ui.py')}
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,scenes=scenes,
        start=args.start,width=args.width,graphics=args.graphics,mode=args.mode,host=host,frames=args.frames,guest=hashes(out/'run.log'),
        binary_sha256=digest(binary),source_sha256=source,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        loaded_states=False,guest_fixture_edits=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(args.start,args.width,args.graphics,args.mode,host,result['result'],checks,scenes,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
