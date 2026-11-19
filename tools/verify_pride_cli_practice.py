"""Verify CLI-loaded practice readiness without changing guest or audio replay."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=('native','md'),required=True);args=parser.parse_args()
    base=ROOT/'build/pride-cli-practice';build_path=base/'build-report.json';build=bound(build_path)
    out=base/args.case;out.mkdir();md=args.case=='md';checks={};observations={};commands={}
    profile=out/'resources.ini';author_profile=ROOT/'build/pride-source-live/seeded/resources.ini'
    profile.write_bytes(author_profile.read_bytes() if md else b'schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';owned=2002 if md else 2001
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda f:[(int(n),v,w) for n,v,w in re.findall(pattern,(f/'run.log').read_text())]
    def run(variant,name,mode,load=None):
        folder=out/variant/name;folder.mkdir(parents=True);binary=base/(variant+'.exe')
        assert digest(binary)==build['runs'][variant]['binary_sha256']
        config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,'--input',tape,'--frames',3000,'--speedrun','practice','--no-audio','--no-record','--no-pace','--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,3001)))]
        if load:command+=['--load',load]
        else:command+=['--save-at',owned,folder/'owned.state']
        if mode=='lle':command+=['--lle']
        env=environment(folder);env.update(TLK_CLI_PRACTICE_LOG=str(folder/'frontend.json'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'md-commands.csv'))
        commands[variant+'/'+name]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[variant+'/'+name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        assert not r.returncode,(variant,name,r.returncode)
        log=(folder/'run.log').read_text();assert 'Profile rejected' not in log and 'MD sound library unavailable' not in log
        observations[variant+'/'+name]=json.loads((folder/'frontend.json').read_text())
        # Preserve large three-plane research records losslessly between runs.
        for path in folder.rglob('*.rgb'):
            subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        print(args.case,variant,name,'exit0',flush=True);return folder
    authors={};resumed={}
    for variant in ('before','after'):
        author=run(variant,'author','lle' if md else 'aot');authors[variant]=author
        automatic=author/'tlk_practice_restart.state';assert automatic.exists()
        for label,state in (('ordinary',automatic),('owned',author/'owned.state')):
            data=state.read_bytes();assert data[:8] in (b'PRPRAC01',b'PRHSAVE1')
            saved=struct.unpack_from('<I',data,20 if data[:8]==b'PRPRAC01' else 16)[0]
            # Owned header stores the timeline at20 too; validate against the
            # actual loader's first observed guest boundary below.
            if label=='owned':saved=owned
            folder=run(variant,label,'aot' if md else 'lle',state);resumed[variant,label]=folder
            first=observations[variant+'/'+label]
            checks[variant+'/'+label+'/loaded_timeline']=first['field']==first['frontend']==saved
            checks[variant+'/'+label+'/practice_enabled']=first['practice']==1
            checks[variant+'/'+label+'/readiness']=first['state'] in (1,2) if variant=='after' else first['state']==0
            if variant=='after':checks[variant+'/'+label+'/unranked']=first['eligible']==0 and first['dirty']==1 and first['loading']==0
            checks[variant+'/'+label+'/endpoint']=hashes(folder/'run.log')==hashes(author/'run.log')
            checks[variant+'/'+label+'/every_native_field']=rows(folder)==[r for r in rows(author) if r[0]>saved] and len(rows(folder))==3000-saved
            boundary=[r for r in read_rows(author/'practice-fields.csv') if int(r['field'])==saved+1];assert len(boundary)==1
            cut=int(boundary[0]['wav_frames_before_audio'])*4
            checks[variant+'/'+label+'/complete_pcm_tail']=wav_data(folder/'audio.wav')==wav_data(author/'audio.wav')[cut:]
            checks[variant+'/'+label+'/remaining_stems']=read_rows(folder/'stems.csv')==[r for r in read_rows(author/'stems.csv') if int(r['frame'])>saved]
            checks[variant+'/'+label+'/save_unchanged']=state.read_bytes()==data
            if md:checks[variant+'/'+label+'/audible_md']=any(int(r['md_peak'])>0 for r in read_rows(folder/'stems.csv'))
    for label in ('ordinary','owned'):
        a,b=resumed['before',label],resumed['after',label]
        checks[label+'/before_after_guest']=rows(a)==rows(b)
        checks[label+'/before_after_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
        w,h,pa=pixels(a/'window.png');bw,bh,pb=pixels(b/'window.png');assert (w,h)==(bw,bh)
        extra=(w//2-256)//2
        checks[label+'/client_outside_practice_panel']=all(x==y for i,(x,y) in enumerate(zip(pa,pb)) if not (2<=i//w//2<22 and 58<=i%w//2-extra<198))
    checks['cold_author_guest_unchanged']=rows(authors['before'])==rows(authors['after'])
    checks['cold_author_pcm_unchanged']=wav_data(authors['before']/'audio.wav')==wav_data(authors['after']/'audio.wav')
    paths=[Path(__file__),build_path,author_profile,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,observations=observations,commands=commands,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                binaries_sha256={v:build['runs'][v]['binary_sha256'] for v in ('before','after')},
                complete_practice_panel_pixel_oracle=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
