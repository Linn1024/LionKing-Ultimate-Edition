"""Resume real default/checkpoint revival and post-ready input in a new process."""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import frame_records, glyph_records
from run_pride_actor_handoff_matrix import CONTEXTS
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-handoff-state'


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--context',choices=tuple(CONTEXTS),default='md-polled')
    p.add_argument('--width',type=int,choices=(256,320),default=320)
    p.add_argument('--graphics',choices=('native','frames','palette','cub','hud','all'),default='native')
    p.add_argument('--save-at',type=int,default=2330)
    p.add_argument('--save-mode',choices=('aot','lle'),default='aot')
    p.add_argument('--load-mode',choices=('aot','lle'),default='lle')
    p.add_argument('--sdl',action='store_true')
    p.add_argument('--output-root',type=Path,default=BASE/'pilot')
    args=p.parse_args();out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    start,route,kind,ready,end=CONTEXTS[args.context]
    assert args.save_at<end
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text())
    host='sdl' if args.sdl else 'probe'
    binary=BASE/f'handoff-state-{host}.exe';assert digest(binary)==build['runs'][host]['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    reference=ROOT/'build/pride-actor-handoff/active'/f'{args.context}-{args.width}-{args.graphics}-aot-owned'
    profile=out/'resources.ini';profile.write_bytes((reference/'resources.ini').read_bytes())
    tape=reference/('checkpoint.polled.tape' if route=='checkpoint' else 'default-neutral.tape')
    state=out/'revival.private-state';results={};commands={}
    source=[Path(__file__),ROOT/'tools/probe_pride_preparation_state.py',build_path,reference/'report.json',tape,reference/'resources.ini']
    sources={str(s.relative_to(ROOT)).replace('\\','/'):digest(s) for s in source}
    resume_tape=out/'resume.tape'
    for name,load in (('baseline',False),('resumed',True)):
        folder=out/name;folder.mkdir(exist_ok=True);env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--frames',end,'--input-polled' if kind=='polled' else '--input',
            resume_tape if load and kind=='polled' else tape]
        if args.sdl:
            config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            command+=['--config',config,'--no-pace','--no-audio','--no-record',
                '--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds','100']
        else:command+=['--ram-log',folder/'route.ram','--wide',args.width,'--wide-png',folder/'picture.png']
        command+=['--load',state] if load else ['--save-at',args.save_at,state]
        if (args.load_mode if load else args.save_mode)=='lle':command+=['--lle']
        commands[name]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        results[name]=dict(exit_code=run.returncode,guest=hashes(folder/'run.log'),
            artifacts_sha256={f.name:digest(f) for f in folder.iterdir() if f.is_file()})
        print(name,'exit',run.returncode,flush=True)
        assert run.returncode==0,(name,run.returncode)
        if not load and kind=='polled':
            ram=[line.split() for line in ((reference if args.sdl else folder)/'route.ram').read_text().splitlines()]
            observed=int(re.search(r'(?:tape_words_used|polls_seen)=(\d+)',(folder/'run.log').read_text())[1])
            assert sum(r[1]=='0' for r in ram)==observed
            cut=sum(r[1]=='0' for r in ram if int(r[0])<=args.save_at)
            resume_tape.write_bytes(tape.read_bytes()[cut*2:])
    checks={}
    a,b=out/'baseline',out/'resumed'
    checks['guest']=results['baseline']['guest']==results['resumed']['guest'] and len(results['baseline']['guest'])==2
    original=json.loads((reference/'report.json').read_text())
    checks['prior_guest']=results['baseline']['guest']==original['guest']
    if not args.sdl:
        checks['prior_tracked_ram']=digest(a/'route.ram')==digest(reference/'route.ram')
        checks['prior_scene_trace']=digest(a/'render-owned.rgb')==digest(reference/'render-owned.rgb')
        before=(a/'route.ram').read_bytes().splitlines(keepends=True)
        after=(b/'route.ram').read_bytes().splitlines(keepends=True)
        checks['remaining_tracked_ram']=after==before[-len(after):] and len(after)==end-args.save_at
    begin=int(next(r for r in rows(a/'owner-events.csv') if r['event']=='begin')['field'])
    expected={age:data for age,data in frame_records(a/'render-owned.rgb',args.width).items() if begin+age>args.save_at}
    checks['remaining_scene_pixels']=frame_records(b/'render-owned.rgb',args.width)==expected
    for filename in ('owner-events.csv','render-fields.csv','prepared-objects.csv','restore-fields.csv','restore-events.csv',
                     'post-ready.csv','normal-owner.csv','spawn-policy.csv'):
        expected=[r for r in rows(a/filename) if int(r['field'])>args.save_at] if (a/filename).exists() else []
        actual=rows(b/filename) if (b/filename).exists() else []
        checks[filename]=actual==expected
    checks['remaining_glyphs']=glyph_records(b)==[(f,r) for f,r in glyph_records(a) if f>args.save_at]
    checks['final_image']=pixels(a/('window.png' if args.sdl else 'picture.png'))==pixels(b/('window.png' if args.sdl else 'picture.png'))
    if args.sdl:
        baseline,resumed=wav_data(a/'audio.wav'),wav_data(b/'audio.wav')
        checks['native_pcm_tail']=len(resumed)>0 and baseline[-len(resumed):]==resumed
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,runs=results,
        context=args.context,host=host,width=args.width,graphics=args.graphics,save_at=args.save_at,save_mode=args.save_mode,load_mode=args.load_mode,
        binary_sha256=digest(binary),source_sha256=sources,state_sha256=digest(state),commands=commands,
        loaded_state_only_from_current_ordinary_run=True,guest_fixture_edits=False,public_player_enabled=False,
        full_first_level_fidelity_complete=False)
    for path,sha in sources.items():assert digest(ROOT/path)==sha,path
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
