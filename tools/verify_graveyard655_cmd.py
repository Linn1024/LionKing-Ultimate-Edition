"""Exercise the actual new CMD, capture its Windows client, and record the applied MD choices."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
publication=ROOT/'build/graveyard654-publication/report.json';bound(publication);out=ROOT/'build/graveyard655-cmd';out.mkdir();trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();captured=False
cmd=[os.environ['COMSPEC'],'/d','/c',str(ROOT/'Play Elephant Graveyard MD.cmd'),'-Frames','2000','-NoPace','-NoAudio','-WindowCapture',str(out/'window.png'),'-SceneCapture',str(out/'scene.json')];ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+35
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row and row['field']>=1500 and row['level']==2 and row['descriptor']==0xc003eb and not captured:
                query=subprocess.check_output([ps,'-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name='LionKing.exe'\" | Select-Object -ExpandProperty ProcessId"],creationflags=subprocess.CREATE_NO_WINDOW,text=True)
                for pid in query.split():
                    hwnd=window_for(int(pid))
                    if hwnd:capture_client(hwnd,out/'actual-client.png');captured=True;break
            time.sleep(.008)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        trace.finish()
last=trace.latest();c={x[0]:x for x in last['choices']};scene=json.loads((out/'scene.json').read_text());checks=dict(cmd_exits_cleanly=proc.returncode==0,real_client=captured,living_graveyard=scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['health']>0,md_graphics_audio_gameplay=all(c[x][4]==2 for x in ('game','graphics.scenery.foreground','graphics.sprites.enemies.vultures.frames','audio.music.elephant_graveyard.death','audio.effects.world.graveyard.pillar','gameplay.levels.elephant_graveyard.vulture_health','gameplay.levels.elephant_graveyard.vulture_bounds')),separate_settings=(ROOT/'settings/graveyard-md/resources.ini').exists())
paths=[Path(__file__),publication,ROOT/'Play Elephant Graveyard MD.cmd',ROOT/'profiles/graveyard-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
