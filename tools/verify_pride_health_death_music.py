"""Verify independent health-death music, revival and exact audio continuation.

Actual Windows player, ordinary credited controller prefix and neutral tail.
No practice menu, loaded checkpoints or actor/world edits in complete runs.
Save/load cases are separate continuation proofs. Fall/game-over remain separate.
"""
import csv
import hashlib
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import audio_offset, seal, wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-health-death-music';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    original_path=ROOT/'build/pride-health-death-original/report.json'
    original=json.loads(original_path.read_text());assert original['result']=='PASS'
    assert original['original_death_music']==430 and original['original_level_music_after_revival']==137
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    source=ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape'
    zero=out/'neutral.polled.tape';zero.write_bytes(bytes(8000))
    profiles={}
    for name,extra in {'native':'','level':'audio.music.pride_lands = md\n',
                       'death':'audio.music.pride_health_death = md\n',
                       'both':'audio.music.pride_lands = md\naudio.music.pride_health_death = md\n'}.items():
        profile=out/(name+'.ini');profile.write_text('schema = 1\ngame = snes\n'+extra);profiles[name]=profile

    def run(name,profile,extra=(),state=None,expect=0):
        folder=out/name;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env.update(TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),
            TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'))
        cmd=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
             '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profiles[profile],
             '--config',config,'--frames','5400','--input-polled',zero if state else source,
             '--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json',*extra]
        if state:cmd+=['--load',state]
        with (folder/'run.log').open('wb') as f:
            result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
        assert result.returncode==expect,(name,result.returncode,(folder/'run.log').read_text()[-1200:])
        return folder

    runs={};pictures={};gameplay={}
    for name in profiles:
        modes={};waves=[]
        for mode in ('aot','lle'):
            saved=out/(name+'-4500.state')
            extra=(['--lle'] if mode=='lle' else ['--save-at','4500',saved])
            folder=run(name+'-'+mode,name,extra)
            commands=list(csv.DictReader((folder/'driver.csv').open()))
            tracks=[int(r['value']) for r in commands if r['selector']=='1']
            if name=='native':assert not commands,'Native profile entered MD driver'
            elif name=='level':assert tracks==[137,137,134,0,137],tracks
            elif name=='death':assert tracks==[430,0],tracks
            else:assert tracks==[137,137,134,430,137],tracks
            scene=json.loads((folder/'scene.json').read_text());guest=scene['latched_gameplay']
            assert scene['stage_detected'] and guest['age']==0,'Revival scene not displayed'
            values=[scene['level'],guest['descriptor'],*guest['player'],guest['health'],guest['lives'],*guest['checkpoint']]
            assert values==[0,0x387,1200,111,6,7,0,1200,112],values
            gameplay[name+'-'+mode]=values
            modes[mode]={'hashes':hashes(folder/'run.log'),'tracks':tracks,'wav_sha256':digest(folder/'route.wav')}
            waves.append(wav_data(folder/'route.wav'))
            pictures[name+'-'+mode]=pixels(folder/'window.png')
        assert modes['aot']==modes['lle'] and waves[0]==waves[1],(name,'Execution modes differ')
        runs[name]=modes
        print(name,'ordinary death/revival, independent tracks and exact AOT/LLE WAV PASS',flush=True)
    assert all(p==pictures['native-aot'] for p in pictures.values()),'Music changed the revived picture'
    saves=[]
    for name,frame,phase in [('level',4300,0),('level',4440,1),('level',4500,2),
                             ('both',4500,2),('level',4800,2),('both',4800,2)]:
        state=out/f'{name}-{frame}.state'
        if frame!=4500:full=run(f'{name}-save-{frame}',name,['--save-at',str(frame),state])
        else:full=out/(name+'-aot')
        raw=state.read_bytes();at=audio_offset(raw)
        assert struct.unpack_from('<I',raw,at+8)[0]==2 and struct.unpack_from('<I',raw,at+112)[0]==phase
        folder=run(f'{name}-loaded-{frame}',name,state=state)
        actual=wav_data(folder/'route.wav');expected=wav_data(full/'route.wav')
        assert actual and expected[-len(actual):]==actual,(name,frame,'Audio continuation differs')
        assert hashes(folder/'run.log')==hashes(full/'run.log'),(name,frame,'Guest continuation differs')
        saves.append({'profile':name,'frame':frame,'phase':phase,'exact_bytes':len(actual)})
        if phase==0:
            legacy=bytearray(raw);struct.pack_into('<I',legacy,at+8,1)
            path=out/'legacy-v1-alive.state';path.write_bytes(seal(legacy))
            prior=run('legacy-v1-alive','level',state=path)
            assert wav_data(prior/'route.wav')==actual and hashes(prior/'run.log')==hashes(folder/'run.log')
        print(name,frame,'saved phase',phase,'exact continuation PASS',flush=True)
    old=ROOT/'build/pride-death-music-before/legacy-death.state'
    if old.exists():
        legacy=run('actual-legacy-death','level',state=old)
        tracks=[int(r['value']) for r in csv.DictReader((legacy/'driver.csv').open()) if r['selector']=='1']
        assert tracks==[0,137],('Legacy battle loop retained',tracks)
    raw=bytearray((out/'both-4500.state').read_bytes());at=audio_offset(raw)
    struct.pack_into('<I',raw,at+112,4);bad=out/'invalid-phase.state';bad.write_bytes(seal(raw))
    run('invalid-phase','both',state=bad,expect=8)
    result={'result':'PASS','scope':__doc__,'player_sha256':digest(ROOT/'dist/LionKing.exe'),
            'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'original_reference_sha256':digest(original_path),'input_sha256':digest(source),
            'runs':runs,'ordinary_power_on_complete_runs':8,'all_profile_revived_pictures_equal':True,
            'revived_gameplay_fields':gameplay,'exact_saved_phases':saves,
            'living_v1_audio_exact':True,'legacy_death_loop_repaired':old.exists(),
            'invalid_phase_rejected':True,'fall_death_or_game_over_verified':False}
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    print('Independent Pride health-death music and continuation PASS',flush=True)


if __name__=='__main__':main()
