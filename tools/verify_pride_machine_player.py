"""Reset an owned mixed revival and compare the entire new run to cold play."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=('native','md'),required=True);args=parser.parse_args()
    base=ROOT/'build/pride-machine-player';build_path=base/'build-report.json';build=bound(build_path)
    binary=base/'machine.exe';assert digest(binary)==build['binary_sha256']
    out=base/args.case;out.mkdir();md=args.case=='md';warm=2002 if md else 2001
    profile=out/'resources.ini';author=ROOT/'build/pride-source-live/seeded/resources.ini';profile.write_bytes(author.read_bytes() if md else b'schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={};observations={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:[(int(n),v,w) for n,v,w in re.findall(pattern,(p/'run.log').read_text())]
    def run(kind,mode):
        name=kind+'-'+mode;folder=out/name;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,'--input',tape,'--frames',3000,'--speedrun','practice','--no-audio','--no-record','--no-pace','--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,3001)))]
        if mode=='lle':cmd+=['--lle']
        env=environment(folder);env.update(TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'md-commands.csv'));env.pop('TLK_MACHINE_RESET_AT',None);env.pop('TLK_CLI_PRACTICE_LOG',None)
        if kind!='cold':env.update(TLK_MACHINE_RESET_AT=str(warm),TLK_MACHINE_RESET_KIND=kind)
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=360)
        assert not r.returncode,(name,r.returncode)
        text=(folder/'run.log').read_text();assert 'Profile rejected' not in text and 'MD sound library unavailable' not in text,name
        for path in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        print(args.case,name,'exit0',flush=True);return folder
    controls={mode:run('cold',mode) for mode in ('aot','lle')}
    checks['cold_modes/guest']=rows(controls['aot'])==rows(controls['lle'])
    checks['cold_modes/pcm']=wav_data(controls['aot']/'audio.wav')==wav_data(controls['lle']/'audio.wav')
    checks['cold_modes/client']=pixels(controls['aot']/'window.png')==pixels(controls['lle']/'window.png')
    scene_names={'render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin','scenery-evidence.json'}
    for kind in ('soft','init'):
        for mode in ('aot','lle'):
            folder=run(kind,mode);name=folder.name;control=controls[mode]
            b=json.loads((folder/'machine-boundary.json').read_text());observations[name]=b
            checks[name+'/owned_boundary']=b['field_before']==warm and b['owner_before']==1 and b['age_before']>200
            checks[name+'/cleared_machine_context']=b['field_after']==b['owner_after']==b['pending_after']==b['bank_ready_after']==b['practice_after']==b['audio_profile_changed']==0
            observed=rows(folder);reference=rows(control)
            checks[name+'/warm_guest_prefix']=observed[:warm]==reference[:warm]
            checks[name+'/every_restarted_native_field']=len(observed)==warm+3000 and observed[warm:]==reference and len(reference)==3000
            mixed=wav_data(folder/'audio.wav');cold=wav_data(control/'audio.wav');cut=b['audio_samples_before']*4
            checks[name+'/warm_pcm_prefix']=mixed[:cut]==cold[:cut]
            checks[name+'/complete_restarted_pcm']=mixed[cut:]==cold
            checks[name+'/whole_client']=pixels(folder/'window.png')==pixels(control/'window.png')
            restarted=folder/'machine-reset-1';assert restarted.is_dir()
            artifacts=[p for p in control.rglob('*') if p.name in scene_names]
            checks[name+'/two_scenery_records']=len([p for p in artifacts if p.name=='scenery-evidence.json'])>=2
            for path in artifacts:
                relative=path.relative_to(control);candidate=restarted/relative
                checks[name+'/scene/'+str(relative).replace('\\','/')]=candidate.exists() and digest(candidate)==digest(path)
            stems=read_rows(folder/'stems.csv');cuts=[i for i in range(1,len(stems)) if int(stems[i]['frame'])<int(stems[i-1]['frame'])]
            if md:
                checks[name+'/audible_warm_md']=bool(cuts) and any(int(r['md_peak'])>0 for r in stems[:cuts[0]])
                checks[name+'/restarted_md_stems']=bool(cuts) and stems[cuts[0]:]==read_rows(control/'stems.csv')
    paths=[Path(__file__),build_path,author,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,observations=observations,commands=commands,binary_sha256=digest(binary),
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        actual_user_reset_control_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
