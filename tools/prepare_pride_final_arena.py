"""Prepare a genuine combined-source prefatal arena checkpoint and old windows."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    route=ROOT/'build/pride-final-arena-route2/report.json';original=bound(route)
    build=ROOT/'build/pride-final-combined/build-report.json';bound(build)
    out=ROOT/'build/pride-final-arena-fixture';out.mkdir();fatal=original['fatal_field']
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\n')
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    commands={}
    def run(name,end,load=None,save=False,enabled=True):
        folder=out/name;folder.mkdir()
        cmd=[ROOT/'build/pride-final-combined/player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',cfg,
            '--input-polled',ROOT/'build/pride-final-arena-route2/ordinary.polled.tape','--frames',end,
            '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        if load:cmd+=['--load',load]
        if save:cmd+=['--save-at',end,folder/'saved.state']
        env=dict(active if enabled else clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'))
        with (folder/'run.log').open('wb') as log:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        commands[name]=list(map(str,cmd));return folder
    ready=run('prefatal',fatal-1,save=True)
    state=ready/'saved.state';assert state.is_file()
    raw=state.read_bytes();n=struct.unpack_from('<I',raw,20)[0]
    inner=out/'prefatal-backend.state';inner.write_bytes(raw[96:96+n])
    # Per-poll playback starts at the first word in a new process. Preserve the
    # actual consumed count from this public player, not the headless estimate.
    import re
    used=int(re.search(r'tape_words_used=(\d+)',(ready/'run.log').read_text()).group(1))
    suffix=out/'after.polled.tape';suffix.write_bytes((ROOT/'build/pride-final-arena-route2/ordinary.polled.tape').read_bytes()[used*2:])
    # Override the captured route suffix in these short checkpoint continuations.
    def branch(name,age,enabled):
        folder=out/name;folder.mkdir();cmd=commands['prefatal'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
        cmd[cmd.index('--frames')+1]=str(fatal+age);cmd[cmd.index('--input-polled')+1]=str(suffix)
        cmd+=['--load',str(state if enabled else inner)]
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json')]:cmd[cmd.index(flag)+1]=str(folder/file)
        env=dict(active if enabled else clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'))
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[name]=cmd
    for age in (0,1):
        branch('control'+str(age),age,False);branch('old'+str(age),age,True)
    paths=[Path(__file__),route,build]
    report=dict(result='PREPARED',fatal_field=fatal,prefix_polls=used,commands=commands,
        old_origin_vs_control=pixels(out/'old0/window.png')==pixels(out/'control0/window.png'),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Arena prefatal prepared',fatal,flush=True)


if __name__=='__main__':main()
