"""Check observer neutrality, then every tracked All Bugs field on player2's core."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'allbugs-observer'
    bp=observer/'build-report.json';build=bound(bp)
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=base/'allbugs2';out.mkdir();profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    reference=ROOT/'build/pride-reset/fixed4/native/gates'
    checks={};commands={};sources=[Path(__file__),bp,base/'build-report.json',tape]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    clean['SDL_VIDEODRIVER']='dummy'
    pattern=r'^(frame_sha256|wram_sha256)=([0-9a-f]+)'
    def run(label,binary,frames,mode,observe):
        folder=out/label;folder.mkdir()
        env=dict(clean)
        if observe:env['TLK_TRACKED_RAM_LOG']=str(folder/'route.ram')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,
             '--md-rom',out/'missing.md','--config',config,'--input-polled',tape,
             '--frames',frames,'--no-pace','--no-audio','--no-record']
        if mode=='lle':cmd+=['--lle']
        commands[label]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            p=subprocess.run(commands[label],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1500)
        assert p.returncode==0,(label,p.returncode)
        hashes=dict(re.findall(pattern,(folder/'run.log').read_text(),re.M));assert len(hashes)==2,label
        print(label,hashes,flush=True)
        return hashes
    pilot_control=run('pilot-control',base/'player.exe',3000,'aot',False)
    pilot_observed=run('pilot-observed',observer/'player.exe',3000,'aot',True)
    checks['pilot_full_frame_wram_neutral']=pilot_control==pilot_observed
    pilot=(out/'pilot-observed/route.ram').read_bytes()
    expected=(reference/'allbugs-aot.ram').read_bytes().splitlines()
    # SDL text output uses CRLF; historical headless output uses LF.
    checks['pilot_every_tracked_field']=pilot.splitlines()==expected[:3000]
    assert all(checks.values()),checks
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={m:pool.submit(run,m,observer/'player.exe',60648,m,True) for m in ('aot','lle')}
        endpoints={m:f.result() for m,f in futures.items()}
    for mode in ('aot','lle'):
        old=reference/f'allbugs-{mode}.ram';sources.append(old)
        data=(out/mode/'route.ram').read_bytes()
        checks[mode+'/all_60648_tracked_fields']=len(data.splitlines())==60648 and data.splitlines()==old.read_bytes().splitlines()
        checks[mode+'/full_frame_endpoint']=endpoints[mode]['frame_sha256']=='0326bd99ae26d38d67e782f83f4fbf2a3d2ec956a78d4cf7533f93668cab1cb5'
        checks[mode+'/full_wram_endpoint']=endpoints[mode]['wram_sha256']=='a0930247992cac1ea728412f4386001df57154c2635ece64e7e8717f02e26f9e'
    checks['aot_lle_every_tracked_field']=(out/'aot/route.ram').read_bytes()==(out/'lle/route.ram').read_bytes()
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        compared_fields=60648,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
