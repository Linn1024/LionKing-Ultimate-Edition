"""Exercise unmodified ordinary, owned and boot saves across resource-editor builds."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_source_controls import macro_tape
from verify_windows import pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=('native','md'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-save-identity';build_path=base/'build-report.json';build=bound(build_path)
    out=base/'verified'/args.profile;out.mkdir(parents=True);md=args.profile=='md'
    source_profile=ROOT/'build/pride-source-live/seeded/resources.ini';profile=out/'resources.ini';profile.write_bytes(source_profile.read_bytes() if md else b'schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';raw_tape=out/'level-select.raw';raw_tape.write_bytes(macro_tape(bytes(6000)))
    checks={};commands={};authored={};owned=2002 if md else 2001;fields_compared=0
    def fields(folder):return re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
    def run(name,variant,end,load=None,save=None,boot=False):
        folder=out/name;folder.mkdir(parents=True);exe=base/(variant+'.exe');assert digest(exe)==build['runs'][variant]['binary_sha256']
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,
             '--frames',end,'--no-audio','--no-record','--no-pace','--speedrun','practice','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
             '--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,end+1)))]
        if boot and load:cmd+=['--input-raw',raw_tape]
        else:cmd+=['--input',tape]
        if boot and not load:cmd+=['--practice-level','0']
        if md:cmd+=['--lle']
        if load:cmd+=['--load',load]
        if save:cmd+=['--save-at',owned,save]
        commands[name]=list(map(str,cmd));env=environment(folder);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv');env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv');env['TLK_SOFT_TREE_LOG']=str(folder/'presents.jsonl')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        for file in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        return folder,r.returncode
    for variant in ('a','b'):
        target=out/('author-'+variant)/'owned.state';folder,code=run('author-'+variant,variant,3000,save=target);assert not code,variant
        ordinary=folder/'tlk_practice_restart.state';assert ordinary.read_bytes()[:8]==b'PRPRAC01' and target.read_bytes()[:8]==b'PRHSAVE1'
        boot_folder,code=run('boot-author-'+variant,variant,2,boot=True);assert not code
        boot=boot_folder/'tlk_practice_boot.state';assert boot.read_bytes()[:8]==b'PRHBOOT1'
        authored[variant]=dict(ordinary=ordinary,owned=target,boot=boot)
        for kind,state in authored[variant].items():checks[variant+'/'+kind+'/explicit_identity']=state.read_bytes()[24:56].hex()==build['runs'][variant]['save_compatibility_sha256']
        print(args.profile,variant,'authored ordinary/owned/boot',flush=True)
    a,b=out/'author-a',out/'author-b';checks['cold/every_guest_field']=fields(a)==fields(b) and len(fields(a))==3000;fields_compared+=3000
    checks['cold/full_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    checks['cold/whole_client']=pixels(a/'window.png')==pixels(b/'window.png')
    checks['cold/md_stems']=read_rows(a/'stems.csv')==read_rows(b/'stems.csv')
    for origin,destination in (('a','b'),('b','a')):
        for kind in ('ordinary','owned','boot'):
            state=authored[origin][kind];before=digest(state);saved=0 if kind=='boot' else int.from_bytes(state.read_bytes()[20:24],'little')
            end=1800 if kind=='ordinary' else 3000 if kind=='owned' else 1500
            folders=[]
            for name,variant in (('control',origin),('cross',destination)):
                folder,code=run(origin+'-to-'+destination+'/'+kind+'/'+name,variant,end,load=state,boot=kind=='boot');assert not code,(kind,origin,name,code);folders.append(folder)
            a,b=folders;label=origin+'-to-'+destination+'/'+kind
            checks[label+'/unmodified_input']=digest(state)==before
            checks[label+'/all_guest_fields']=fields(a)==fields(b) and len(fields(b))==end-saved;fields_compared+=end-saved
            checks[label+'/complete_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav') and bool(wav_data(a/'audio.wav'))
            checks[label+'/whole_client']=pixels(a/'window.png')==pixels(b/'window.png')
            checks[label+'/whole_guest']=pixels(a/'guest.png')==pixels(b/'guest.png')
            checks[label+'/all_md_stems']=read_rows(a/'stems.csv')==read_rows(b/'stems.csv')
            for filename in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json'):
                checks[label+'/'+filename]=(a/filename).exists()==(b/filename).exists() and (not (a/filename).exists() or digest(a/filename)==digest(b/filename))
            if kind!='boot':
                cold=out/('author-'+origin);expected=[r for r in fields(cold) if saved<int(r[0])<=end]
                checks[label+'/native_cold_suffix']=fields(b)==expected
                journal=read_rows(cold/'practice-fields.csv');first=next(r for r in journal if int(r['field'])==saved+1)
                next_row=next((r for r in journal if int(r['field'])==end+1),None)
                lo=int(first['wav_frames_before_audio'])*4;hi=int(next_row['wav_frames_before_audio'])*4 if next_row else len(wav_data(cold/'audio.wav'))
                checks[label+'/complete_cold_pcm_suffix']=wav_data(b/'audio.wav')==wav_data(cold/'audio.wav')[lo:hi]
            bad,code=run(label+'/wrong-epoch','incompatible',end,load=state,boot=kind=='boot')
            checks[label+'/incompatible_epoch_rejected']=code==8 and 'cannot load state ' in (bad/'run.log').read_text()
            checks[label+'/rejection_preserves_file']=digest(state)==before
            print(args.profile,label,'replayed and wrong epoch rejected',flush=True)
    paths=[Path(__file__),build_path,source_profile,tape,ROOT/'tools/verify_pride_source_controls.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=fields_compared,
                save_compatibility_sha256=build['runs']['a']['save_compatibility_sha256'],binary_sha256={name:r['binary_sha256'] for name,r in build['runs'].items()},
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                public_player_enabled=False,legacy_migration_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.profile,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
