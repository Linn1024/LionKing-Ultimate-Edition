"""Check that death music commands retain the playing MD hurt-audio timeline.

Ordinary controller replay saves on both sides of the song/stop boundaries.
The real nested audio envelope must advance its ring and fractional resampler
by the exact number of output samples; resetting it would skip selected FX.
"""
import csv
import hashlib
import json
import math
import os
import struct
import subprocess
import wave
from audit_scenes import ROOT
from verify_pride_audio_state import audio_offset


def main():
    out=ROOT/'build/pride-death-fx-timeline';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    results={}
    # Source-specific native SPC queue timing can move Music Off by a field;
    # bracket the observed event rather than borrowing the native-hurt frame.
    for name,frames,last_track in [('death',(4429,4430),430),('native-stop',(4492,4500),0)]:
        profile=out/(name+'.ini')
        profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.simba.hurt = md\n'+
                           ('audio.music.pride_health_death = md\n' if name=='death' else ''))
        snapshots=[]
        for frame in frames:
            stem=out/f'{name}-{frame}';state=stem.with_suffix('.state')
            env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(stem)+'.csv'
            cmd=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                 '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
                 '--config',config,'--frames',str(frame),'--input-polled',ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape',
                 '--no-pace','--no-audio','--no-record','--wav',str(stem)+'.wav','--wav-seconds','100',
                 '--save-at',str(frame),state]
            with stem.with_suffix('.log').open('wb') as f:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
            raw=state.read_bytes();at=audio_offset(raw);native=struct.unpack_from('<I',raw,at+44)[0];md=at+128+native
            assert raw[md:md+8]==b'TLKMDS01'
            with wave.open(str(stem)+'.wav','rb') as wav:count=wav.getnframes();output_rate=wav.getframerate()
            commands=list(csv.DictReader(stem.with_suffix('.csv').open()))
            assert any(r['selector']=='19' and r['value']=='1' for r in commands),'Selected hurt voice not triggered'
            tracks=[int(r['value']) for r in commands if r['selector']=='1']
            if frame==frames[-1]:assert tracks[-1]==last_track,tracks
            snapshots.append({'frame':frame,'read':struct.unpack_from('<Q',raw,md+24)[0],
                              'write':struct.unpack_from('<Q',raw,md+16)[0],
                              'phase':struct.unpack_from('<d',raw,md+32)[0],
                              'rate':struct.unpack_from('<d',raw,md+40)[0],
                              'output_samples':count,'output_rate':output_rate,
                              'state_sha256':hashlib.sha256(raw).hexdigest()})
        before,after=snapshots;produced=after['output_samples']-before['output_samples']
        assert produced>0 and before['rate']==after['rate']
        advance=before['phase']+produced*before['rate']/before['output_rate']
        expected_read=before['read']+math.floor(advance)
        assert after['read']==expected_read,('FX ring skipped/reset',name,snapshots,expected_read)
        assert abs(after['phase']-(advance-math.floor(advance)))<1e-8,('FX resampler phase reset',name,snapshots)
        results[name]={'snapshots':snapshots,'output_sample_delta':produced,'exact_timeline_advance':True}
        print(name,'selected hurt voice and exact MD ring/resampler continuity PASS',flush=True)
    report={'result':'PASS','scope':__doc__,'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'cases':results,'loaded_states':False,'guest_or_rom_edits':False}
    report_path.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
