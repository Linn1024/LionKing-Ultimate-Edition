"""Exercise independent checkpoint animation from genuine current-build contact."""
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
    base=ROOT/'build/pride-checkpoint-animation51';buildpath=base/'build-report.json';build=bound(buildpath)
    referencepath=ROOT/'build/pride-checkpoint-native51-reference/report.json';reference=bound(referencepath)
    out=base/'animation-play';out.mkdir();commands={};checks={}
    template=reference['commands']['contact'].copy();template[0]=str(base/'player.exe')
    i=template.index('--save-at');del template[i:i+3]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    neutral=out/'neutral.tape';neutral.write_bytes(bytes(4096))
    def run(label,end,source='md',seed=None,lle=False,capture=True):
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]=str(end)
        profile=Path(template[template.index('--resource-profile')+1]).read_text()
        profile+='\ngameplay.levels.pride_lands.checkpoint_animation = '+source+'\n'
        (folder/'resources.ini').write_text(profile)
        (folder/'host.ini').write_bytes(Path(template[template.index('--config')+1]).read_bytes())
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/name)
        if seed:
            cmd+=['--load',str(seed)];cmd[cmd.index('--input-polled')+1]=str(neutral)
        else:cmd+=['--save-at','3280',str(folder/'contact.state')]
        if lle:cmd+=['--lle']
        cmd+=['--hash-at',','.join(map(str,range(1,end+1)))]
        if not capture:
            i=cmd.index('--dump-window');del cmd[i:i+2]
        commands[label]=cmd
        env=dict(clean,TLK_CHECKPOINT_TIMING_TRACE=str(folder/'timing.csv'),TLK_CONTINUE_TOKEN_TIMING_TRACE=str(folder/'sun.csv'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        assert rc==0,(label,(folder/'run.log').read_text()[-500:])
        print(label,'completed',flush=True);return folder
    with ThreadPoolExecutor(max_workers=2) as pool:
        seeds=dict(zip(('native','md'),pool.map(lambda source:run(source+'-contact',3280,source),('snes','md'))))
    # The native source must retain every fresh field and the real contact image.
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    old=referencepath.parent/'contact'
    for name in ('window.png','scene.json','audio.wav'):
        checks['native_contact_'+name]=digest(seeds['native']/name)==digest(old/name)
    checks['native_hook_inactive']=not (seeds['native']/'timing.csv').exists()
    checks['md_initial_wait_installed']=(seeds['md']/'timing.csv').exists()
    def branch(lle):return run('cycles-'+('lle' if lle else 'aot'),3970,'md',seeds['md']/'contact.state',lle,False)
    with ThreadPoolExecutor(max_workers=2) as pool:a,b=pool.map(branch,(False,True))
    checks['all690_guest_fields_mode_parity']=len(hashes(a))==690 and hashes(a)==hashes(b)
    for name in ('scene.json','audio.wav','timing.csv','sun.csv','events.csv'):
        exists=(a/name).exists() and (b/name).exists()
        checks['cycles_'+name+'_mode_parity']=exists and digest(a/name)==digest(b/name)
    traces=list(csv.DictReader((a/'timing.csv').open()))
    checks['three_blink2_cycles_observed']=sum(r['pc']=='c0ad54' and r['value']=='20' for r in traces)>=3
    checks['md_one_time_initialization']=len(list(csv.DictReader((seeds['md']/'timing.csv').open())))==1
    # Completed display fields relative to contact3280: base through+6, then
    # blink1 six, blink2 twentyone, blink1 six, base188. Sample every boundary.
    fields=[3286,3287,3292,3293,3313,3314,3319,3320,3507,3508,3514,3535,3541,3729]
    def capture(field):
        folder=run('display-'+str(field),field,'md',seeds['md']/'contact.state')
        scene=json.loads((folder/'scene.json').read_text())
        poses=sorted({p['pose'] for p in scene['pieces'] if p['pose'] in (0xc456de,0xc2fde1,0xc2fe18)})
        offset=(field-3287)%221
        expected=0xc2fde1 if offset<6 or 27<=offset<33 else 0xc2fe18 if offset<27 else 0xc456de
        return field,poses,expected
    with ThreadPoolExecutor(max_workers=3) as pool:captures=list(pool.map(capture,fields))
    for field,poses,expected in captures:checks['display_'+str(field)]=poses==[expected]
    paths=[Path(__file__),buildpath,referencepath,ROOT/'build/pride-checkpoint-timing51-qualification/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                captures=[dict(field=f,poses=p,expected=e) for f,p,e in captures],
                no_guest_or_rom_edits=True,cross_build_save_compatibility_tested=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
