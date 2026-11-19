"""Observe active Pride porcupines on complete native and mixed route replays."""
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
    out=ROOT/'build/pride-porcupine-lifetimes';out.mkdir()
    source=ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json';prior=bound(source)
    build_path=ROOT/'build/pride-sprite-fresh44/porcupine-lifetime-observer/build-report.json';build=bound(build_path)
    assert build['nonhost_inputs_unchanged']==321 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    selector_path=ROOT/'build/pride-nonpersistent-selector/report.json';selector=bound(selector_path);assert selector['result']=='PASS'
    rejected={r['attribute'] for r in selector['cases'] if r['index']==2 and r['native'][0]==r['md']==0}
    template=prior['commands']['full-aot'];commands={};checks={};cases={};folders={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for label,observe,native,lle in [('mixed-aot',True,False,False),('mixed-lle',True,False,True),
                                     ('native-control',False,True,False),('native-aot',True,True,False),('native-lle',True,True,True)]:
        folder=out/label;folder.mkdir();folders[label]=folder;cmd=template.copy()
        if observe:cmd[0]=str(build_path.parent/'player.exe')
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if native:
            (folder/'resources.ini').write_text('schema = 1\ngame = snes\n')
            cmd[cmd.index('--input-polled')+1]=str(ROOT/'engine/tapes/allbugsF.read.tape')
        if lle:cmd.append('--lle')
        commands[label]=cmd
        env=dict(clean,TLK_PORCUPINE_LIFETIME_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                 TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0
        last=json.loads((folder/'tree.jsonl').read_text().splitlines()[-1]);checks[label+'_completes_pride']=last['level']==1 and last['health']>0
        if observe:
            text=(folder/'actors.csv').read_text();checks[label+'_valid_active_list']='INVALID_ACTIVE_LIST' not in text
            rows=list(csv.DictReader(text.splitlines()));attacks=[r for r in rows if r['action']=='c15b87']
            checks[label+'_natural_attacks_seen']=bool(attacks)
            checks[label+'_all_attacks_persistent']=bool(attacks) and all(r['persistent']=='1' for r in attacks)
            checks[label+'_all_attributes_reject_nonpersistent']=bool(rows) and all(int(r['attribute']) in rejected for r in rows)
            cases[label]=dict(active_rows=len(rows),attack_rows=len(attacks),facings=sorted({int(r['facing']) for r in rows}),
                              attack_facings=sorted({int(r['facing']) for r in attacks}),
                              attributes=sorted({int(r['attribute']) for r in rows}),
                              actor_slots=sorted({r['actor'] for r in rows}),
                              persistent_values=sorted({int(r['persistent']) for r in attacks}),last=last)
        print(label,rc,'final level',last['level'],cases.get(label,{}).get('attack_rows'),flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    samples=lambda p:re.findall(pattern,(p/'run.log').read_text())
    reference=source.parent/'full-aot'
    for label,left,right in [('mixed_observer_neutral',reference,folders['mixed-aot']),
                              ('mixed_modes',folders['mixed-aot'],folders['mixed-lle']),
                              ('native_observer_neutral',folders['native-control'],folders['native-aot']),
                              ('native_modes',folders['native-aot'],folders['native-lle'])]:
        checks[label+'_all6000_guest_fields']=len(samples(left))==6000 and samples(left)==samples(right)
        for name in ('window.png','scene.json','audio.wav','events.csv','attack.csv','tree.jsonl'):
            checks[label+'_'+name]=digest(left/name)==digest(right/name)
        if label in ('mixed_modes','native_modes'):
            checks[label+'_active_actor_fields']=digest(left/'actors.csv')==digest(right/'actors.csv')
    paths=[Path(__file__),source,build_path,selector_path]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,cases=cases,
                active_linked_list_only=True,ordinary_poweron_replays=True,guest_or_rom_edits=False,
                universal_dynamic_unreachability_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
