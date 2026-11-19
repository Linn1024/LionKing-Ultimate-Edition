"""Paced WASAPI playback with selectable music and native guest preservation."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output65';bp=base/'build-report.json';build=bound(bp)
    source=base/'completion/report.json';prior=bound(source);assert prior['result']=='PASS'
    native_source=ROOT/'build/pride-music-output62/allbugs-verification/report.json';native=bound(native_source);assert native['result']=='PASS'
    out=base/'audio-device';out.mkdir();checks={};commands={};observations={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    expected=re.findall(pattern,(native_source.parent/'pilot-control/run.log').read_text())[:1500]
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    for choice,mode in [('native','aot'),('music','aot'),('music','lle')]:
        name=choice+'-'+mode;folder=out/name;folder.mkdir();cmd=prior['commands']['aot'].copy()
        cmd.remove('--no-pace');cmd.remove('--no-audio');cmd[cmd.index('--frames')+1]='1500'
        cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,1501)));cmd[cmd.index('--input-polled')+1]=str(tape)
        (folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+('audio.music.pride_lands = md\n' if choice=='music' else ''))
        (folder/'host.ini').write_text('opengl = 0\nscale = 1\naudio = 1\naudio_rate = 48000\nvolume = 100\n')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd+=['--lle']
        commands[name]=cmd
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_AUDIO_DRIVER='wasapi',TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_AUDIO_QUEUE_TRACE=str(folder/'queue.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        log=(folder/'run.log').read_text();rows=re.findall(pattern,log)
        stats=re.search(r'frames=1500 wall_s=([\d.]+) fps=([\d.]+) audio_underruns=(\d+) late_resyncs=(\d+)',log);assert stats
        queue=list(csv.DictReader((folder/'queue.csv').open()))
        stems=list(csv.DictReader((folder/'stems.csv').open()))
        driver=list(csv.DictReader((folder/'driver.csv').open()));tracks=[int(r['value']) for r in driver if r['selector']=='1']
        with wave.open(str(folder/'audio.wav'),'rb') as w:frames,rate,channels=w.getnframes(),w.getframerate(),w.getnchannels()
        checks[name+'_exit']=rc==0
        checks[name+'_all1500_native_guest_fields']=len(rows)==1500 and rows==expected
        checks[name+'_paced']=float(stats[1])>=1500/(21477272/357366)*.9
        checks[name+'_opened_wasapi_queue']=bool(queue) and any(int(r['paused'])==0 and int(r['queued_frames'])>0 for r in queue) and 'continuing without sound' not in log
        checks[name+'_no_reported_underruns']=int(stats[3])==0
        checks[name+'_stereo48k_pcm']=frames>0 and rate==48000 and channels==2
        checks[name+'_music_choice_observed']=(137 in tracks and all(t==137 for t in tracks)) if choice=='music' else not tracks
        checks[name+'_audible_selected_md_stem']=any(int(r['md_peak'])>500 for r in stems) if choice=='music' else not stems
        observations[name]=dict(wall_seconds=float(stats[1]),fps=float(stats[2]),underruns=int(stats[3]),late_resyncs=int(stats[4]),
            wav_stereo_frames=frames,queue_rows=len(queue),md_tracks=tracks)
        print(name,observations[name],'failures',[k for k,v in checks.items() if not v],flush=True)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source,native_source,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='actual WASAPI opened-stream, queued playback and rendered PCM; no physical speaker recording',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
