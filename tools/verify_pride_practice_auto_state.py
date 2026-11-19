"""Resume actual automatic practice saves through both later revivals."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import frame_records,glyph_records
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes,pixels


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=('native','md'),default='native');p.add_argument('--sdl',action='store_true',default=True)
    p.add_argument('--output-root',type=Path)
    args=p.parse_args();assert not (args.sdl and args.case=='cross-frames')
    base=ROOT/'build/pride-practice'
    out=(ROOT/args.output_root if args.output_root else base/'final')/'windows-auto-state'/args.case
    out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists(),'Use a fresh proof directory'
    start,width,graphics,save,load=('md',320,'all','lle','aot') if args.case=='md' else ('snes',256,'native','aot','lle')
    selected_width=320 if args.case=='cross-frames' else width
    selected_graphics='frames' if args.case=='cross-frames' else graphics
    reference_root=ROOT/'build/pride-repeat'/('scoped-windows' if args.sdl else 'scoped-headless')
    reference=reference_root/f'{start}-{width}-{graphics}-{save}'
    expected=reference_root/f'{start}-{selected_width}-{selected_graphics}-{save}'
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());host='sdl' if args.sdl else 'probe';binary=base/f'practice-{host}.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs'][host]['binary_sha256']
    profile=out/'resources.ini';profile.write_bytes((reference/'resources.ini').read_bytes())
    selected=out/'selected.ini';selected.write_bytes((expected/'resources.ini').read_bytes())
    author_path=base/'verified/normal-ui'/('md-lle' if args.case=='md' else 'native-aot')/'report.json'
    author=json.loads(author_path.read_text());assert author['result']=='PASS'
    state=author_path.parent/'automatic-original.state';saved=author['observations']['automatic_saved_field'];tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={}
    def run(name,mode,resources,view,extra):
        folder=out/name;folder.mkdir(exist_ok=True)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',resources,'--input',tape,'--frames',3000]+extra
        if mode=='lle':command+=['--lle']
        if args.sdl:
            config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            command+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                '--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100]
        else:command+=['--wide',view,'--wide-png',folder/'picture.png','--ram-log',folder/'route.ram']
        commands[name]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[name],cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=240)
        assert not r.returncode,(name,r.returncode)
        return folder
    before=run('baseline',save,profile,width,[])
    after=run('resumed',load,selected,selected_width,['--load',state])
    checks=dict(ordinary_format=state.read_bytes()[:8]==b'PRPRAC01',guest=hashes(before/'run.log')==hashes(after/'run.log'),
        preceding_guest=hashes(before/'run.log')==hashes(reference/'run.log'))
    second=2458 if start=='md' else 2459
    for folder,prior,label in ((before,reference,'baseline-first'),(before/f'scene-{second}',reference/f'scene-{second}','baseline-second'),
        (after/'restart-1',expected,'loaded-first'),(after/f'restart-1/scene-{second}',expected/f'scene-{second}','loaded-second')):
        checks[label+'/rgb']=digest(folder/'render-owned.rgb')==digest(prior/'render-owned.rgb')
        checks[label+'/glyphs']=glyph_records(folder)==glyph_records(prior)
        checks[label+'/ground']=digest(folder/'ground-return.bin')==digest(prior/'ground-return.bin')
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv'):
        checks[name]=read_rows(after/name)==[r for r in read_rows(before/name) if int(r['field'])>saved]
    image='window.png' if args.sdl else 'picture.png'
    checks['final_image']=pixels(after/image)==pixels(expected/image)
    if args.sdl:
        rows=read_rows(before/'practice-fields.csv');boundary=[r for r in rows if int(r['field'])==saved+1];assert len(boundary)==1
        cut=int(boundary[0]['wav_frames_before_audio'])*4
        a,b=wav_data(before/'audio.wav'),wav_data(after/'audio.wav')
        checks['native_pcm_tail']=a[cut:]==b
        checks['preceding_pcm']=a==wav_data(reference/'audio.wav')
    else:
        a=(before/'route.ram').read_bytes().splitlines(keepends=True);b=(after/'route.ram').read_bytes().splitlines(keepends=True)
        checks['remaining_ram']=len(b)==1500 and b==a[-1500:]
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,author_path,state,reference/'report.json',expected/'report.json',tape,
        ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py')}
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,host=host,
        save_mode=save,load_mode=load,saved_field=saved,binary_sha256=digest(binary),source_sha256=sources,commands=commands,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(args.case,host,result['result'],[n for n,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
