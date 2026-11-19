"""One current Available MD save/resume through the fight and level finish."""
import json,os,re,subprocess,time,wave
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride406-preset-route/report.json';ref=bound(reference);assert ref['result']=='PASS'
build=ROOT/'build/pride398/build-report.json';b=bound(build)
out=ROOT/'build/pride411-save';out.mkdir(exist_ok=True)
player=ROOT/'dist/installed-preview398/LionKing.exe';assert digest(player)==b['binary_sha256']
data=ROOT/'game-data';manifest=json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
keys=(('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets'))
base=ref['command'].copy();base[0]=str(player);i=base.index('--save-at');del base[i:i+3]
for flag,key in keys:base[base.index(flag)+1]=str(data/manifest[key]['file'])
for flag,key in (('--rom','snes'),('--md-rom','megadrive')):base[base.index(flag)+1]=str(data/manifest['roms'][key]['file'])
def command(label,frames,hashes):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[cmd.index('--frames')+1]=str(frames);cmd[cmd.index('--hash-at')+1]=hashes
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    return cmd
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
seed=command('seed',3600,'1500,2200,3600');state=out/'seed/current.state';seed+=['--save-at','3600',str(state)]
with (out/'seed/run.log').open('wb') as log:seed_rc=subprocess.run(seed,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=log,stderr=subprocess.STDOUT,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW).returncode
assert seed_rc==0 and state.is_file()
used=int(re.search(r'tape_words_used=(\d+)',(out/'seed/run.log').read_text())[1]);original=Path(base[base.index('--input-polled')+1]).read_bytes()
tail=out/'remaining.polled.tape';tail.write_bytes(original[used*2:]);assert tail.stat().st_size
resume=command('resume',6000,'4500,6000');resume[resume.index('--input-polled')+1]=str(tail);resume+=['--load',str(state)]
USER32.SetProcessDPIAware();reader=None;before=after=None
with (out/'resume/run.log').open('wb') as log:
    proc=subprocess.Popen(resume,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(player,proc.pid);deadline=time.monotonic()+60
        def snapshot():
            row=reader.snapshot();ram=reader.base+reader.symbols['_g_ram'];row['descriptor']=int.from_bytes(reader.read(ram+0xdf,3),'little');row['level']=int.from_bytes(reader.read(ram+0x1ff9e,2),'little');return row
        while proc.poll() is None and time.monotonic()<deadline:
            before=snapshot()
            if before['field']>=3650:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'resumed-arena.png');after=snapshot();break
            time.sleep(.005)
        proc.wait(timeout=90)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
def pcm(path):
    with wave.open(str(path),'rb') as audio:
        assert audio.getnchannels()==2 and audio.getsampwidth()==2 and audio.getframerate()==48000
        return audio.readframes(audio.getnframes())
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda path:re.findall(pattern,path.read_text())
baseline=rows(reference.parent/'run.log');seed_rows=rows(out/'seed/run.log');resume_rows=rows(out/'resume/run.log')
seed_pcm=pcm(out/'seed/audio.wav');baseline_pcm=pcm(reference.parent/'audio.wav');resume_pcm=pcm(out/'resume/audio.wav')
scene=json.loads((out/'resume/scene.json').read_text());initial=json.loads((out/'seed/scene.json').read_text())
checks=dict(seed_exit=seed_rc==0,ordinary_live_arena_checkpoint=initial['level']==0 and initial['stage_detected'] and initial['latched_gameplay']['descriptor']==0x80d,seed_guest_prefix_preserved=[r for r in seed_rows if r[0] in ('1500','2200')]==[r for r in baseline if r[0] in ('1500','2200')],seed_pcm_prefix_preserved=seed_pcm==baseline_pcm[:len(seed_pcm)],correct_polled_tail=tail.read_bytes()==original[used*2:],resume_exit=proc.returncode==0,resumed_guest_endpoints=resume_rows==[r for r in baseline if r[0] in ('4500','6000')],resumed_picture=digest(out/'resume/window.png')==digest(reference.parent/'window.png'),resumed_pcm=resume_pcm==baseline_pcm[len(seed_pcm):],first_level_completed=scene['level']==1,all_spare_lives_retained=scene['latched_gameplay']['lives']==8,actual_resumed_window=bool(after) and 3650<=before['field']<=after['field']<3894 and before['level']==after['level']==0 and before['descriptor']==after['descriptor']==0xc0080d)
paths=[Path(__file__),reference,build,data/'install.json',player,Path(base[base.index('--input-polled')+1])]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=dict(seed=seed,resume=resume),seed_polled_words=used,before=before,after=after,scope='One current published player/default installed-data full Available MD save during ordinary Easy arena play, cold resume with the actual remaining polled input, actual Windows view, fight/level completion and audio continuation. No old-save, source, width or mode matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,'seed polls',used,flush=True)
