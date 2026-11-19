"""Qualify read-only music ownership observations on the Difficult fight."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-owner59';bp=base/'build-report.json';build=bound(bp)
    source=ROOT/'build/pride-music-transport59/verification/report.json';prior=bound(source)
    assert prior['result']=='PASS'
    out=base/'verification';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(mode):
        folder=out/mode;folder.mkdir();cmd=prior['commands']['music-'+mode].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[mode]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_MUSIC_OWNER_TRACE=str(folder/'owner.csv')),
                              stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        return mode,(folder,rc)
    with ThreadPoolExecutor(max_workers=2) as pool:runs=dict(pool.map(run,('aot','lle')))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    for mode,(folder,rc) in runs.items():
        reference=source.parent/('music-'+mode)
        checks[mode+'_exit']=rc==0
        checks[mode+'_all4600_guest_fields_neutral']=len(hashes(folder))==4600 and hashes(folder)==hashes(reference)
        for file in ('scene.json','window.png','audio.wav'):checks[mode+'_'+file+'_neutral']=digest(folder/file)==digest(reference/file)
        rows=list(csv.DictReader((folder/'owner.csv').open()))
        software=[r for r in rows if r['stage']=='software'];assign=[r for r in rows if r['stage']=='assign']
        keyon=[r for r in rows if r['stage']=='keyon' and r['scene'] in ('12583815','12584973') and r['level']=='0']
        # Decimal scenes are C00387 and C0080D.
        keyon=[r for r in rows if r['stage']=='keyon' and int(r['scene']) in (0xc00387,0xc0080d) and r['level']=='0']
        music=[r for r in software if r['group']=='224']
        checks[mode+'_program0_eight_channels_each_start']=bool(music) and all(r['program']=='0' for r in music) and all(n==8 for n in Counter((r['field'],r['stream']) for r in music).values())
        checks[mode+'_music_both_pride_scenes']=set(int(r['scene']) for r in music)>={0xc00387,0xc0080d}
        checks[mode+'_all_other_programs_group0']=all(r['group']=='0' for r in software if r['program']!='0')
        checks[mode+'_all_assignment_groups_known']=all(r['group'] in ('0','224') for r in assign)
        checks[mode+'_all_pride_keyon_groups_known']=bool(keyon) and all(r['group'] in ('0','224') for r in keyon)
        checks[mode+'_pride_music_and_effect_keyons']=set(r['group'] for r in keyon)=={'0','224'}
        observations[mode]=dict(rows=len(rows),software_groups=dict(Counter(r['group'] for r in software)),
            pride_keyon_groups=dict(Counter(r['group'] for r in keyon)),
            program_groups=[dict(program=p,group=g,count=n) for (p,g),n in sorted(Counter((r['program'],r['group']) for r in software).items())],
            music_starts=[dict(field=int(f),stream=int(s),channels=n) for (f,s),n in Counter((r['field'],r['stream']) for r in music).items()])
    checks['complete_owner_trace_mode_parity']=digest(runs['aot'][0]/'owner.csv')==digest(runs['lle'][0]/'owner.csv')
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    original=ROOT/'build/pride-lizard-launch-work/player/spc-owner-audit/native/aram_1400.bin';ram=original.read_bytes()
    checks['original_group_parameter_store']=ram[0xfc7:0xfcc]==bytes.fromhex('e4 0b d5 e3 02')
    paths=[Path(__file__),bp,source,original]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                read_only_observer=True,dual_music_intentional=True,production_output_filter=False,
                other_scenes_death_continue_or_all_music_unproven=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    print(json.dumps(observations,indent=2),flush=True)


if __name__=='__main__':main()
