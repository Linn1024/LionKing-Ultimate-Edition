"""Exercise current Pride backgrounds during paused edits and same-build reloads.

Three ordinary route positions, both widths, controller input only. This checks
background source/history lifecycle, not new original layer/edge equivalence.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client

NODE='graphics.scenery.background'


def main():
    out=ROOT/'build/pride-background-lifecycle54';out.mkdir()
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source)
    binding=ROOT/'build/pride-checkpoint-capability53/bindings/report.json';assert bound(binding)['result']=='PASS'
    template=prior['commands']['aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    i=template.index('--dump-window');del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    commands={};checks={};observations={};USER32.SetProcessDPIAware()
    def case(item):
        width,point=item;name=f'{width}-{point}';folder=out/name;folder.mkdir();end=point+30
        profile=Path(template[template.index('--resource-profile')+1]).read_text() if width==320 else (
            'schema = 1\ngame = snes\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.sprites.enemies = md\ngraphics.hud = md\n')
        profile+='\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n'+NODE+' = md\n'
        tape=Path(template[template.index('--input-polled')+1]) if width==320 else ROOT/'engine/tapes/allbugsF.read.tape'
        def command(stage):
            target=folder/stage;target.mkdir();cmd=template.copy()
            for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(target/file)
            (target/'resources.ini').write_text(profile);(target/'host.ini').write_text('opengl = 0\nscale = 2\n')
            cmd[cmd.index('--frames')+1]=str(end);cmd[cmd.index('--input-polled')+1]=str(tape)
            cmd+=['--hash-at',','.join(map(str,range(point,end+1)))]
            env=dict(clean,TLK_SOFT_TREE_LOG=str(target/'tree.jsonl'),TLK_BG_TRACE=str(target/'background.csv'))
            commands[name+'/'+stage]=cmd
            return target,cmd,env
        control,cmd,env=command('control');state=control/'current.state';cmd+=['--save-at',str(point),str(state)]
        env['SDL_VIDEODRIVER']='dummy'
        with (control/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW)
        live,cmd,env=command('live');cmd+=['--menu-at',str(point),'--menu-page','resources']
        hwnd=None;snapshots={};images={}
        with (live/'run.log').open('wb') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            def wait(predicate,timeout=180):
                deadline=time.monotonic()+timeout
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(live/'tree.jsonl')
                    if row and predicate(row):return row
                    time.sleep(.02)
                raise AssertionError((name,proc.poll(),latest(live/'tree.jsonl')))
            def key(vk):
                scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
                assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
                assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
            def selected(row):return next(c for c in row['choices'] if c[0]==NODE)
            def capture(label):
                row=latest(live/'tree.jsonl');snapshots[label]=row
                capture_client(hwnd,live/(label+'.png'));images[label]=pixels(live/(label+'.png'))
                return row
            try:
                before=wait(lambda r:r['about']==2 and r['field']==point);hwnd=window_for(proc.pid);assert hwnd
                checks[name+'_ordinary_pride_context']=before['level']==0 and before['descriptor'] in (0xc00387,0xc0080d) and before['health']>0
                key(0x24)
                for _ in range(180):
                    row=latest(live/'tree.jsonl');node=row['choices'][row['selected']][0]
                    if node==NODE:break
                    if node=='game' or NODE.startswith(node+'.'):key(0x27)
                    key(0x28)
                else:raise AssertionError('background node unreachable')
                capture('initial-md')
                for label,value in [('native-1',1),('restored-1',2),('native-2',1),('restored-2',2)]:
                    for _ in range(3):
                        if selected(latest(live/'tree.jsonl'))[1]==value:break
                        key(0x0d)
                    key(0x71);wait(lambda r:r['modal']==1);key(0x1b)
                    row=wait(lambda r:r['dirty']==0 and selected(r)[-1]==value)
                    capture(label)
                checks[name+'_paused_through_source_changes']=all(r['field']==point for r in snapshots.values())
                checks[name+'_restores_identical_client_twice']=images['initial-md']==images['restored-1']==images['restored-2']
                checks[name+'_native_client_repeatable']=images['native-1']==images['native-2']
                checks[name+'_actual_client_dimensions']=images['initial-md'][:2]==(width*2,448)
                # Ignore the resource panel and header/footer, retaining the
                # outside world strips and top/bottom. UI labels cannot satisfy
                # this evidence of changed scene pixels.
                w,h,a=images['initial-md'];b=images['native-1'][2];margin=(width-256)//2
                changed=sum(a[y*w+x]!=b[y*w+x] for y in range(h) for x in range(w)
                            if x<(margin+8)*2 or x>=(margin+248)*2 or y<8*2 or y>=216*2)
                checks[name+'_background_changes_outside_ui']=changed>0
                observations[name]=dict(snapshots=snapshots,changed_world_strip_pixels=changed)
                key(0x7b);proc.wait(timeout=240);assert proc.returncode==0
            finally:
                if proc.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        rows=[json.loads(line) for line in (control/'tree.jsonl').read_text().splitlines()]
        start=next(r for r in rows if r['field']==point)
        suffix=folder/'remaining.polled.tape';suffix.write_bytes(tape.read_bytes()[start['poll_index']*2:])
        resume,cmd,env=command('resume');cmd+=['--load',str(state)];cmd[cmd.index('--input-polled')+1]=str(suffix);env['SDL_VIDEODRIVER']='dummy'
        with (resume/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
        hashes=lambda target:re.findall(pattern,(target/'run.log').read_text())
        checks[name+'_live_all31_guest_fields']=len(hashes(control))==31 and hashes(live)==hashes(control)
        checks[name+'_resume_all30_guest_fields']=hashes(resume)==[r for r in hashes(control) if int(r[0])>point]
        checks[name+'_live_entire_pcm_unchanged']=digest(live/'audio.wav')==digest(control/'audio.wav')
        checks[name+'_live_scene_unchanged']=digest(live/'scene.json')==digest(control/'scene.json')
        checks[name+'_resume_scene_unchanged']=digest(resume/'scene.json')==digest(control/'scene.json')
        print(name,'completed',[k for k,v in checks.items() if k.startswith(name) and not v],flush=True)
    cases=[(width,point) for width in (256,320) for point in (1200,2200,4000)]
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(case,cases))
    paths=[Path(__file__),source,binding,ROOT/'tools/windows_capture.py',ROOT/'docs/background-audit.md']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                source_changes_are_live=True,same_build_resume_only=True,cross_build_save_compatibility_tested=False,
                original_layer_or_edge_recipe_changed=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
