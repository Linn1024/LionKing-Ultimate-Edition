"""Paced WASAPI output with guest equality and actual selected MD bounce stems."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound


def main():
    base=ROOT/'build/pride-bounce-owner-work/player';public=ROOT/'build/pride-lizard-launch-work/player'
    bp=base/'build-report.json';build=bound(bp);assert digest(base/'player.exe')==build['binary_sha256']
    rp=base/'verification/report.json';assert bound(rp)['result']=='PASS'
    out=base/'audio-device';out.mkdir();checks={};commands={};measurements={}
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\naudio = 1\naudio_rate = 48000\nvolume = 100\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    expected=re.findall(pattern,(base/'verification/native-aot/run.log').read_text())[:1500]
    for profile,mode in (('native','aot'),('bounce','aot'),('bounce','lle')):
        label=profile+'-'+mode;folder=out/label;folder.mkdir()
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        env.update(SDL_AUDIO_DRIVER='wasapi',TLK_AUDIO_STEMS=str(folder/'stems.csv'),
            TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_SEMANTIC_OWNER_TRACE=str(folder/'ownership.csv'))
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',config,
            '--resource-profile',public/f'launch-audio/{profile}.ini','--input-polled',tape,
            '--frames',1500,'--no-record','--hash-at',','.join(map(str,range(1,1501))),
            '--wav',folder/'audio.wav','--wav-seconds',40,'--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=160)
        log=(folder/'run.log').read_text();rows=re.findall(pattern,log)
        stats=re.search(r'frames=1500 wall_s=([\d.]+) fps=([\d.]+) audio_underruns=(\d+) late_resyncs=(\d+)',log)
        assert stats
        with wave.open(str(folder/'audio.wav'),'rb') as wav:
            sample_frames=wav.getnframes();rate=wav.getframerate();channels=wav.getnchannels()
        with (folder/'driver.csv').open() as stream:driver=list(csv.DictReader(stream))
        with (folder/'stems.csv').open() as stream:stems=list(csv.DictReader(stream))
        with (folder/'ownership.csv').open() as stream:owners=list(csv.DictReader(stream))
        count=sum(r['selector']=='2' and r['value']=='123' for r in driver)
        checks[label+'/every_native_guest_field']=rows==expected
        checks[label+'/paced_run']=float(stats[1])>=1500/(21477272/357366)*.9
        checks[label+'/wasapi_not_rejected']='continuing without sound' not in log and env['SDL_AUDIO_DRIVER']=='wasapi'
        # Only an opened astream applies this device-queue servo to WAV samples.
        fixed=int(1500*48000/(21477272/357366))
        checks[label+'/opened_stream_servo_observed']=abs(sample_frames-fixed)>2
        checks[label+'/stereo_48k']=rate==48000 and channels==2
        checks[label+'/no_underruns']=int(stats[3])==0
        checks[label+'/two_selected_requests']=count==(2 if profile=='bounce' else 0)
        checks[label+'/two_owned_keyons']=sum(r['stage']=='keyon' for r in owners)==2
        if profile=='bounce':
            for start,end in ((1398,1408),(1430,1440)):
                checks[f'{label}/audible_md_stem_{start}']=any(start<=int(r['frame'])<=end and int(r['md_peak'])>0 for r in stems)
        else:checks[label+'/no_md_stem']=not stems
        measurements[label]=dict(wall_s=float(stats[1]),fps=float(stats[2]),underruns=int(stats[3]),
            late_resyncs=int(stats[4]),device_sample_frames=sample_frames,fixed_sample_frames=fixed,md_fm123=count)
        print(label,measurements[label],'failed',[k for k,v in checks.items() if not v],flush=True)
    sources=[Path(__file__),bp,rp,tape,config]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,measurements=measurements,
        scope='WASAPI opened-stream/queue/render evidence, not a physical speaker recording',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'real audio checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
