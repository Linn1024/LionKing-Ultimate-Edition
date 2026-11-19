"""Real draft preset, branch/leaf overrides, Apply and playable restart."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from windows_capture import capture_client
from windows_json_pipe import JsonPipe
reference=ROOT/'build/pride392-route/report.json';ref=bound(reference)
build=ROOT/'build/pride398/build-report.json';bound(build)
out=ROOT/'build/pride399-ui';out.mkdir(exist_ok=True);cmd=ref['commands']['after'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,n in (('--input-polled',2),('--wav',2)):
    i=cmd.index(flag);del cmd[i:i+n]
cmd.remove('--no-pace');cmd[cmd.index('--frames')+1]='12000';cmd[cmd.index('--hash-at')+1]='1500'
cmd+=['--practice-level','0','--menu-at','1500','--menu-page','resources']
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
checks={};snapshots={};hwnd=None;USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate,seconds=60):
        deadline=time.monotonic()+seconds
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row and predicate(row):return row
            time.sleep(.008)
        raise AssertionError(('UI state missing',proc.poll(),trace.latest()))
    def key(vk):
        scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
        assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
    def choices(row):return {c[0]:c for c in row['choices']}
    def select(node):
        key(0x24)
        for _ in range(180):
            row=trace.latest();name=row['choices'][row['selected']][0]
            if name==node:return row
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        raise AssertionError(('node missing',node))
    try:
        initial=wait(lambda r:r['about']==2 and r['field']==1500);hwnd=window_for(proc.pid);assert hwnd
        snapshots['initial']=initial;capture_client(hwnd,out/'initial.png');original=profile.read_bytes()
        key(0x76);draft=wait(lambda r:r['modal'] and choices(r)['game'][1]==2);snapshots['preset']=draft;capture_client(hwnd,out/'preset.png')
        d=choices(draft)
        supported=('graphics.sprites.simba.cub.frames','graphics.scenery.background','audio.music.pride_lands','gameplay.simba.roar','gameplay.levels.pride_lands.start','gameplay.hitboxes.simba','gameplay.levels.pride_lands.final_life')
        unsupported=('graphics.sprites.simba.adult.frames','gameplay.simba.movement','gameplay.simba.combat','gameplay.levels.other','audio.voices')
        checks['available_choices_selected']=all(d[name][3]==2 for name in supported)
        checks['unavailable_choices_explicit_snes']=all(d[name][1]==d[name][3]==1 for name in unsupported)
        checks['preset_is_draft_only']=all(c[2:5:2]==choices(initial)[c[0]][2:5:2] for c in draft['choices']) and profile.read_bytes()==original
        checks['paused_guest_held']=draft['field']==initial['field'] and draft['health']==initial['health']
        key(0x1b);select('graphics');key(0x0d);row=wait(lambda r:choices(r)['graphics'][1]==1);snapshots['branch']=row
        c=choices(row);checks['branch_inheritance_preserved']=c['graphics.sprites.simba.cub.frames'][1]==0 and c['graphics.sprites.simba.cub.frames'][3]==1 and c['audio.music.pride_lands'][3]==2 and c['gameplay.simba.roar'][3]==2
        select('graphics.sprites.simba.cub.frames');key(0x0d);key(0x0d);row=wait(lambda r:choices(r)['graphics.sprites.simba.cub.frames'][1]==2);snapshots['leaf']=row
        c=choices(row);checks['independent_leaf_override']=c['graphics.sprites.simba.cub.frames'][3]==2 and c['graphics.sprites.simba.cub.palette'][3]==1 and c['graphics.hud.frames'][3]==1
        capture_client(hwnd,out/'override.png');key(0x71);restart=wait(lambda r:not r['menu'] and r['field']<1000);snapshots['restart']=restart
        after=wait(lambda r:r['field']>=2200 and r['descriptor']==0xc00387 and r['health']>0 and r['macro_index']==r['macro_length']);snapshots['after']=after;capture_client(hwnd,out/'gameplay.png')
        c=choices(after);text=profile.read_text();checks['applied_and_persisted']=c['game'][-1]==2 and c['graphics'][-1]==1 and c['graphics.sprites.simba.cub.frames'][-1]==2 and 'game = md' in text and 'graphics = snes' in text and 'graphics.sprites.simba.cub.frames = md' in text
        checks['playable_restart']=after['health']>0 and after['difficulty']==initial['difficulty']
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish();(out/'trace-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,scope='One actual Windows SDL resource edit: preset stays draft/paused, unsupported leaves explicitly native, branch inheritance and individual override, persist/Apply and playable restart. No gameplay engine change or unrelated route/mode/save matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
