"""Reproduce cold-cache Continue, then verify the next final-life episode."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels,hashes


def main():
    base=ROOT/'build/pride-final-scene-rearm-probe';out=base/'cold-repeat';out.mkdir()
    build=bound(base/'build-report.json')
    old=ROOT/'build/pride-final-scene-lifecycle-probe';bound(old/'build-report.json')
    reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(reference)
    warm=old/'second-episode-oscillating';bound(warm/'report.json')
    tape=warm/'two-episodes.tape';after=out/'cold600.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};commands=[]
    def run(name,binary,end,load,save=None):
        folder=out/name;folder.mkdir();cmd=report['commands'][0].copy();cmd[0]=str(binary)
        i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd[cmd.index('--frames')+1]=str(end);cmd[cmd.index('--input')+1]=str(tape);cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(end),str(save)]
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        # Deliberately omit TLK_CONTINUE_BANK_RECORD in every process.
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd);print(name,'completed',flush=True);return folder
    author=run('author',old/'player.exe',3894+600,ROOT/'build/pride-final-continue-fixture/prefatal.state',after)
    raw=after.read_bytes();ns=struct.unpack_from('<I',raw,20)[0];offset=96+ns+96
    mask=struct.unpack_from('<I',raw,offset+16)[0];confirmed=struct.unpack_from('<Q',raw,offset+52)[0]
    assert mask==511 and confirmed==0,(mask,confirmed)
    bank=list(csv.DictReader((author/'bank.csv').open()))
    assert any(r['event']=='apply' and r['ok']=='0' for r in bank)
    assert any(r['event']=='capture' and r['ok']=='1' for r in bank)
    route=run('route',base/'player.exe',3894+5000,after)
    events=list(csv.DictReader((route/'points.csv').open()))
    fatal=next(r for r in events if r['pc']=='c089b9' and r['spares']=='0' and r['descriptor']=='c00387')
    second=int(fatal['field']);print('cold-path next final-life field',second,flush=True)
    broken=run('broken100',old/'player.exe',second+100,after)
    fixed_state=out/'fixed100.state';fixed=run('fixed100',base/'player.exe',second+100,after,fixed_state)
    direct=run('direct144',base/'player.exe',second+144,after)
    resumed=run('resume144',base/'player.exe',second+144,fixed_state)
    old_event=next(r for r in csv.DictReader((broken/'points.csv').open()) if r['pc']=='c089b9' and r['spares']=='0')
    raw=fixed_state.read_bytes();ns=struct.unpack_from('<I',raw,20)[0];metadata=96+ns+96
    field,entry,age,flags=struct.unpack_from('<4I',raw,metadata)
    checks=dict(cold_native_fallback_proven=True,previous_owned_clock_absent=confirmed==0,
        completed_reload_saved=mask==511,old_predicate_reproduces_stale_episode=old_event['redirected']=='1',
        fixed_starts_new_episode=fatal['redirected']=='0',new_epoch_saved=entry==second and age==100 and field==second+100,
        fresh_target=bool(flags&4) and bool(flags&8),
        visible_repair=pixels(broken/'window.png')!=pixels(fixed/'window.png'),
        actual_game_over100=pixels(fixed/'window.png')==pixels(warm/'save100/window.png'),
        cold_resume_guest=hashes(resumed/'run.log')==hashes(direct/'run.log'),
        cold_resume_window=pixels(resumed/'window.png')==pixels(direct/'window.png'))
    source=[Path(__file__),base/'build-report.json',old/'build-report.json',reference,warm/'report.json',tape]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,next_fatal_field=second,commands=commands,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
