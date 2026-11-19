"""Qualify private latched-effect observations against the exact public53 route."""
from concurrent.futures import ThreadPoolExecutor
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
    base=ROOT/'build/pride-effect-observer56';buildpath=base/'build-report.json';build=bound(buildpath)
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'verification';out.mkdir();commands={};checks={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(mode):
        folder=out/mode;folder.mkdir();cmd=prior['commands'][mode].copy();cmd[0]=str(base/'player.exe')
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        commands[mode]=cmd
        env=dict(clean,TLK_EFFECT_LATCH_TRACE=str(folder/'unknown.csv'),TLK_EFFECT_LATCH_SUMMARY=str(folder/'summary.json'),
                 TLK_SPRITE_OBJECTS=str(folder/'submitted.csv'),TLK_SPRITE_REPORT=str(folder/'sprites.json'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(mode,rc,flush=True);return mode,folder,rc
    with ThreadPoolExecutor(max_workers=2) as pool:results={mode:(folder,rc) for mode,folder,rc in pool.map(run,('aot','lle'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for mode,(folder,rc) in results.items():
        checks[mode+'_exit']=rc==0
        checks[mode+'_all6000_picture_and_wram_fields_neutral']=len(hashes(folder))==6000 and hashes(folder)==hashes(source.parent/mode)
        for name in ('audio.wav','window.png','scene.json'):checks[mode+'_'+name+'_neutral']=digest(folder/name)==digest(source.parent/mode/name)
        rows=list(csv.DictReader((folder/'unknown.csv').open()));groups={}
        for row in rows:
            key=row['pose']+':hud'+row['hud_role']+':title'+row['title_role']
            item=groups.setdefault(key,dict(pose=row['pose'],hud_role=int(row['hud_role']),title_role=int(row['title_role']),
                first_field=int(row['field']),last_field=0,pieces=0,lit_oam_rows=0,wide_candidate_rows=0,kept_pieces=0,stages=set(),objects=set()))
            item['last_field']=int(row['field']);item['pieces']+=1
            for name in ('lit_oam_rows','wide_candidate_rows'):item[name]+=int(row[name])
            item['kept_pieces']+=int(row['kept']);item['stages'].add(int(row['stage']));item['objects'].add(row['object'])
        for item in groups.values():item['stages']=sorted(item['stages']);item['objects']=sorted(item['objects'])
        observations[mode]=dict(summary=json.loads((folder/'summary.json').read_text()),unknown_groups=list(groups.values()))
        print(mode,json.dumps(observations[mode]),flush=True)
    a=results['aot'][0];b=results['lle'][0]
    for name in ('unknown.csv','summary.json','submitted.csv','sprites.json'):checks[name+'_mode_parity']=digest(a/name)==digest(b/name)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),buildpath,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                observer_only=True,public_preview_unchanged=True,
                lit_rows_are_conservative_candidates_not_final_visible_pixels=True,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
