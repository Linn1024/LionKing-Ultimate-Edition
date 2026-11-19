"""Compare live rejected loads against an uninterrupted ordinary-input control."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_handoff_state import rows
from run_pride_actor_handoff_matrix import CONTEXTS
from verify_pride_handoff_state_rejections import sections,seal,put,word
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-reject-rollback'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--context',choices=tuple(CONTEXTS),default='snes-default')
    p.add_argument('--width',type=int,choices=(256,320),default=256)
    p.add_argument('--graphics',choices=('native','all'),default='native')
    p.add_argument('--save-age',type=int,default=269);p.add_argument('--fault-age',type=int,default=273)
    p.add_argument('--mode',choices=('aot','lle'),default='aot');p.add_argument('--sdl',action='store_true')
    p.add_argument('--variants',nargs='+',choices=('preflight','history','cache','backend','forced'),default=['forced'])
    p.add_argument('--output-root',type=Path,default=BASE/'pilot');args=p.parse_args()
    out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    start,route,kind,ready,end=CONTEXTS[args.context];entry=ready-(345 if args.context=='snes-checkpoint' else 300)
    save_at=entry+args.save_age;fault_at=entry+args.fault_age;assert save_at<fault_at<end
    host='sdl' if args.sdl else 'probe';binary=BASE/f'rollback-{host}.exe'
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs'][host]['binary_sha256']
    reference=ROOT/'build/pride-actor-handoff/active'/f'{args.context}-{args.width}-{args.graphics}-{args.mode}-owned'
    if not reference.exists():reference=reference.parent/f'{args.context}-{args.width}-{args.graphics}-aot-owned'
    profile=reference/'resources.ini';tape=reference/('checkpoint.polled.tape' if route=='checkpoint' else 'default-neutral.tape')
    results={};fixtures={};control=None
    for name in ['control']+args.variants:
        folder=out/name;folder.mkdir(exist_ok=True);env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        env['TLK_REJECT_AT']=str(fault_at);env.pop('TLK_REJECT_FILE',None);env.pop('TLK_REJECT_AFTER_NATIVE_SUCCESS',None)
        if name!='control':
            fixture=folder/'fixture.state';fixture.write_bytes(fixtures[name]);env['TLK_REJECT_FILE']=str(fixture)
            if name=='forced':env['TLK_REJECT_AFTER_NATIVE_SUCCESS']='1'
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--frames',str(end),'--input-polled' if kind=='polled' else '--input',tape,
            '--save-at',str(save_at),folder/'seed.state']
        if args.mode=='lle':command+=['--lle']
        if args.sdl:
            config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            command+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                '--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds','100']
        else:command+=['--wide',str(args.width),'--ram-log',folder/'route.ram','--wide-png',folder/'picture.png']
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        checks={'exit':run.returncode==0};snapshots={}
        for section in ('native','context','history','cache'):
            before,after=folder/f'reject-before.{section}',folder/f'reject-after.{section}'
            checks['unchanged_'+section]=before.exists() and after.exists() and digest(before)==digest(after)
            if before.exists() and after.exists():snapshots[section]=[digest(before),digest(after)]
        event=rows(folder/'rejected-load.csv')[0] if (folder/'rejected-load.csv').exists() else {}
        checks['returned_rejection']=event.get('returned')=='0' and event.get('caller_field')==str(0xdecafbad)
        if name=='forced':checks['successful_native_load_then_error_and_restore']=event.get('backend_calls')=='2' and event.get('backend_successes')=='2' and event.get('injected')=='1'
        elif name=='backend':checks['native_backend_reached']=event.get('native_calls')=='1' and event.get('backend_calls')=='2'
        elif name!='control':checks['rejected_before_native']=event.get('native_calls')=='0'
        if name=='control':
            control=folder
            prior=json.loads((reference/'report.json').read_text())
            checks['prior_guest']=hashes(folder/'run.log')==prior['guest']
            if not args.sdl:checks['prior_scene']=digest(folder/'render-owned.rgb')==digest(reference/'render-owned.rgb')
            if checks['exit']:
                original=(folder/'seed.state').read_bytes();native,hist,hs,cache,cs=sections(original)
                def change(at,value):
                    data=bytearray(original);put(data,at,value);return seal(data)
                bad=bytearray(original);bad[native+36]^=1
                fixtures=dict(preflight=change(8,2),history=change(hist+8,2),cache=change(cache+8,2),backend=seal(bad),forced=original)
        else:
            checks['guest']=hashes(folder/'run.log')==hashes(control/'run.log') and len(hashes(folder/'run.log'))==2
            for file in ('render-owned.rgb','prepared-fonts.bin','owner-events.csv','owner-fields.csv','restore-events.csv',
                         'restore-fields.csv','render-fields.csv','prepared-objects.csv','normal-owner.csv','post-ready.csv','spawn-policy.csv'):
                a,b=folder/file,control/file
                checks[file]=a.exists()==b.exists() and (not a.exists() or digest(a)==digest(b))
            checks['client']=pixels(folder/('window.png' if args.sdl else 'picture.png'))==pixels(control/('window.png' if args.sdl else 'picture.png')) if checks['exit'] else False
            if args.sdl:checks['native_pcm']=wav_data(folder/'audio.wav')==wav_data(control/'audio.wav') if checks['exit'] else False
            else:checks['tracked_ram']=digest(folder/'route.ram')==digest(control/'route.ram') if checks['exit'] else False
        results[name]=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,event=event,snapshots=snapshots,
            exit_code=run.returncode,artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        print(name,results[name]['result'],checks,flush=True)
        if not checks['exit']:break
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),build_path,profile,tape,reference/'report.json',
        ROOT/'tools/verify_pride_handoff_state_rejections.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py')}
    report=dict(result='PASS' if len(results)==1+len(args.variants) and all(r['result']=='PASS' for r in results.values()) else 'INCOMPLETE',
        context=args.context,host=host,width=args.width,graphics=args.graphics,mode=args.mode,save_at=save_at,fault_at=fault_at,
        source_sha256=sources,binary_sha256=digest(binary),cases=results,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if report['result']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
