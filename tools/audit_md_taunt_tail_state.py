"""Measure whether the isolated MD taunt voice survives a new-process save load.

This checks playing-tail continuation, not completion of the whole level.
The original actor state and source profile are retained without game edits.
"""
import csv
import json
import os
import subprocess
import wave
import hashlib
from verify_windows import hashes
from audit_scenes import ROOT


def main():
    out=ROOT/'build/md-taunt-tail-state';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'build/pride-hyena-taunt'
    tape=source/'after.polled.tape'
    assert tape.read_bytes()==bytes(len(tape.read_bytes())), 'This audit uses the ordinary stopped-input suffix'
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.effects.world.hyena_taunt = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    checkpoint=out/'during-voice.state'
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
          '--config',str(config),'--input-polled',str(tape),'--frames','4050','--no-pace','--no-audio','--no-record']
    peaks={}
    for name,state in [('continuous',source/'ready.state'),('resumed',checkpoint)]:
        env=os.environ.copy();env['TLK_AUDIO_STEMS']=str(out/(name+'.csv'))
        command=[*base,'--load',str(state),'--wav',str(out/(name+'.wav')),'--wav-seconds','10']
        if name=='continuous':command+=['--save-at','4030',str(checkpoint)]
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        rows=list(csv.DictReader((out/(name+'.csv')).open()))
        peaks[name]=max((int(row['md_peak']) for row in rows if 4031<=int(row['frame'])<=4050),default=0)
    assert peaks['continuous']>500,'No active original-driver voice tail in fixture'
    preserved=peaks['resumed']>500
    def audio(name):
        with wave.open(str(out/(name+'.wav')),'rb') as wav:
            assert wav.getnchannels()==2 and wav.getframerate()==48000
            return wav.readframes(wav.getnframes())
    continuous,resumed=audio('continuous'),audio('resumed')
    assert resumed and continuous[-len(resumed):]==resumed,'Full mixed WAV continuation differs'
    assert hashes(out/'continuous.log')==hashes(out/'resumed.log'),'Guest continuation differs'
    assert preserved
    result={'result':'PRESERVED' if preserved else 'GAP_CONFIRMED','scope':__doc__,
            'saved_during_original_md_voice':True,'source_profile_unchanged':True,
            'md_voice_peaks_after_saved_field':peaks,'md_tail_preserved':preserved,
            'full_mixed_wav_continuation_exact':True,'continuation_bytes':len(resumed),
            'continuation_sha256':hashlib.sha256(resumed).hexdigest(),
            'expected':'Restore the isolated MD driver/audio continuation when sources match'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
