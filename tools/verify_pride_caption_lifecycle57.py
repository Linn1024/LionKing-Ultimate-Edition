"""Check late caption live edits and a fresh caption after ordinary level restart."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_sprite_catalog import bitmap
from verify_windows import USER32,window_for,pixels
from verify_pride_soft_tree import latest
from windows_capture import capture_client

BRANCH='graphics.titles.pride_lands'


def main():
    out=ROOT/'build/pride-caption-lifecycle57';out.mkdir();checks={};commands={};observations={}
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source)
    template=prior['commands']['aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    USER32.SetProcessDPIAware()
    def make(label,end,loaded=False,ui=False):
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]=str(end)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/file;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if loaded:
            cmd+=['--load',str(out/'seed/current.state')]
            i=cmd.index('--input-polled');del cmd[i:i+2]
        if ui:
            i=cmd.index('--dump-window');del cmd[i:i+2]
            cmd+=['--menu-at','1171','--menu-page','resources']
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        return folder,cmd,env
    seed,cmd,env=make('seed',1170);cmd+=['--save-at','1170',str(seed/'current.state')]
    with (seed/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
    scene=json.loads((seed/'scene.json').read_text());title=[p for p in scene['pieces'] if p['title_owner']]
    checks['seed_in_short_hidden_native_alive_interval']=bool(title) and all(0<p['actor_timer']<=50 for p in title)
    assert checks['seed_in_short_hidden_native_alive_interval'],[(p['actor_timer'],p['pose']) for p in title]
    rompath=ROOT/'Lion King, The (World).md';rom=rompath.read_bytes();parts=[]
    for i in range(11):
        w,h,x,y,flags,transfer,ptr=struct.unpack_from('>6HI',rom,0x1d5dac+24+i*16);parts.append((x-160,y-72,w,h,ptr))
    bx,by,bw,bh,data=bitmap(rom,parts,True,with_origin=True)
    palette=[sum(((c>>s&7)*4+((c>>s&7)>>2))<<(n*5) for n,s in enumerate((1,5,9))) for c in struct.unpack_from('>16H',rom,0x1d78aa)]
    points=[(160+bx+i%bw,72+by+i//bw,palette[c]) for i,c in enumerate(data) if c]
    def original_matches(pic):
        w,h,p=pic
        return sum(p[(y*2)*w+x*2]==tuple(((c>>s&31)<<3)|((c>>s&31)>>2) for s in (0,5,10)) for x,y,c in points)
    def run(label):
        ui=label!='control';folder,cmd,env=make(label,15000 if label=='restart' else 1205,True,ui)
        if label=='restart':cmd.remove('--no-pace')
        else:cmd+=['--hash-at',','.join(map(str,range(1171,1206)))]
        with (folder/'run.log').open('wb') as log:
            if not ui:
                subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);return
            proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            hwnd=None;snapshots={};images={}
            def wait(predicate,timeout=90):
                deadline=time.monotonic()+timeout
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(folder/'tree.jsonl')
                    if row and predicate(row):return row
                    time.sleep(.005)
                raise AssertionError((label,proc.poll(),latest(folder/'tree.jsonl')))
            def key(vk):
                scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
                assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
                assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
            def select(node):
                key(0x24)
                for _ in range(180):
                    row=latest(folder/'tree.jsonl');selected=row['choices'][row['selected']][0]
                    if selected==node:return
                    if selected=='game' or node.startswith(selected+'.'):key(0x27)
                    key(0x28)
                raise AssertionError(('node missing',node))
            def setchoice(node,value):
                select(node)
                for _ in range(3):
                    row=latest(folder/'tree.jsonl')
                    if next(c for c in row['choices'] if c[0]==node)[1]==value:return
                    key(0x0d)
                raise AssertionError(('choice not staged',node))
            def snap(name):
                snapshots[name]=latest(folder/'tree.jsonl');capture_client(hwnd,folder/(name+'.png'))
                images[name]=pixels(folder/(name+'.png'))
            def apply(name):
                key(0x71);wait(lambda r:r['modal']==1);key(0x1b);wait(lambda r:not r['dirty'])
                select(BRANCH+'.duration');snap(name)
            try:
                before=wait(lambda r:r['about']==2 and r['field']==1171);hwnd=window_for(proc.pid);assert hwnd
                if label=='live':
                    select(BRANCH+'.duration');snap('initial-short')
                    setchoice(BRANCH+'.frames',1);apply('native-frames-short')
                    setchoice(BRANCH+'.palette',1);setchoice(BRANCH+'.position',1);apply('native-visual-short')
                    for part in ('frames','palette','position'):setchoice(BRANCH+'.'+part,2)
                    apply('md-visual-short');setchoice(BRANCH+'.duration',1);apply('long-md')
                    setchoice(BRANCH+'.duration',2);apply('short-restored')
                    def caption_delta(name):
                        w,h,a=images['initial-short'];b=images[name][2]
                        return sum(a[(y*2)*w+x*2]!=b[(y*2)*w+x*2] for x,y,_ in points if not 208<=x-32<248)
                    deltas={name:caption_delta(name) for name in images}
                    checks['late_visual_changes_do_not_resurrect_short_caption']=all(deltas[name]==0 for name in ('native-frames-short','native-visual-short','md-visual-short','short-restored'))
                    checks['long_duration_reveals_existing_caption']=deltas['long-md']>100
                    checks['all_live_edits_keep_guest_paused']=all(r['field']==1171 for r in snapshots.values())
                    observations[label]=dict(snapshots=snapshots,caption_region_deltas=deltas)
                    key(0x7b);proc.wait(timeout=120)
                else:
                    setchoice('gameplay.levels.pride_lands.checkpoint_animation',1);key(0x71)
                    wait(lambda r:not r['menu'] and r['field']<300)
                    entry=wait(lambda r:r['descriptor']==0xc00387 and r['health']>0)
                    probes=[];found=False
                    for i in range(100):
                        row=latest(folder/'tree.jsonl');path=folder/f'restart-probe-{i:03d}.png'
                        capture_client(hwnd,path);matches=original_matches(pixels(path));probes.append(dict(field=row['field'],matched_original_md_pixels=matches,path=path.name))
                        if matches==len(points):found=True;break
                        time.sleep(.015)
                    checks['restarted_caption_matches_all1686_original_md_pixels']=found and len(points)==1686
                    checks['restart_retains_difficulty']=entry['difficulty']==before['difficulty']
                    key(0x7b);paused=wait(lambda r:r['about']==2)
                    observations[label]=dict(entry=entry,paused=paused,probes=probes)
                    USER32.PostMessageW(hwnd,0x10,0,0);proc.wait(timeout=10)
                checks[label+'_clean_exit']=proc.returncode==0
            finally:
                if proc.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        print(label,'completed',flush=True)
    run('control')
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,('live','restart')))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
    checks['all35_live_guest_fields_unchanged']=len(hashes('control'))==35 and hashes('control')==hashes('live')
    checks['live_whole_pcm_unchanged']=digest(out/'control/audio.wav')==digest(out/'live/audio.wav')
    checks['live_final_scene_unchanged']=digest(out/'control/scene.json')==digest(out/'live/scene.json')
    restarted=json.loads((out/'restart/scene.json').read_text());owned=[p for p in restarted['pieces'] if p['title_owner']]
    checks['restarted_caption_has_fresh_timer']=bool(owned) and max(p['actor_timer'] for p in owned)>50
    paths=[Path(__file__),source,rompath,ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                actual_public_binary=True,same_build_seed_only=True,cross_build_save_compatibility_tested=False,
                original_fade_timing_equivalence_verified=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
