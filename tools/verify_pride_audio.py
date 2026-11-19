"""Verify independent first-level MD music/roar through actual player captures.

Run scripts/Verify.ps1 first to prepare the native first-level savestate.
Generated recordings remain local under build/pride-audio-verification/.
"""
import array
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT

def main():
    dest=ROOT/'build/pride-audio-verification';dest.mkdir(parents=True,exist_ok=True)
    state=ROOT/'build/windows-smoke/level.state'
    if not state.exists():raise RuntimeError('Run scripts/Verify.ps1 to prepare the native state')
    actions=array.array('H',[0]*500)
    for i in range(30,50):actions[i]=0x0080 # SNES A: default roar
    (dest/'roar.tape').write_bytes(actions.tobytes())
    (dest/'hurt.tape').write_bytes(array.array('H',[0x0100]*300+[0]*600).tobytes())
    results={}
    for name,choices,extra in [
        ('idle','audio.music.pride_lands = md\n',['--practice-level','0','--frames','2500','--wav-seconds','50']),
        ('snes-roar','audio.music.pride_lands = md\n',['--load',str(state),'--frames','2450','--input-polled',str(dest/'roar.tape'),'--wav-seconds','10']),
        ('md-roar','audio.music.pride_lands = md\naudio.effects.simba.roar = md\n',['--load',str(state),'--frames','2450','--input-polled',str(dest/'roar.tape'),'--wav-seconds','10']),
        ('snes-hurt','audio.music.pride_lands = md\n',['--load',str(state),'--frames','2450','--input-polled',str(dest/'hurt.tape'),'--wav-seconds','10']),
        ('md-hurt','audio.music.pride_lands = md\naudio.effects.simba.hurt = md\n',['--load',str(state),'--frames','2450','--input-polled',str(dest/'hurt.tape'),'--wav-seconds','10']),
        ('md-lizard','audio.music.pride_lands = md\naudio.effects.world.lizard = md\n',['--load',str(state),'--frames','2450','--input-polled',str(dest/'hurt.tape'),'--wav-seconds','10'])]:
        profile=dest/(name+'.ini');profile.write_text('schema = 1\ngame = snes\n'+choices)
        env=os.environ.copy();env['TLK_AUDIO_STEMS']=str(dest/(name+'.csv'))
        env['TLK_AUDIO_EVENTS']=str(dest/(name+'-events.csv'))
        cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(ROOT/'build/windows-smoke/host.ini'),
             '--resource-profile',str(profile),'--no-pace','--no-audio','--no-record',
             '--wav',str(dest/(name+'.wav')),*extra]
        with (dest/(name+'.log')).open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        rows=list(csv.DictReader((dest/(name+'.csv')).open()))
        assert rows,name+' did not render MD audio'
        results[name]=rows
    assert all(int(x['native_peak'])==0 for x in results['idle'][-100:]),'native music was not isolated'
    assert max(int(x['md_peak']) for x in results['idle'][-100:])>1000,'MD music is silent'
    roar=lambda name:[x for x in results[name] if 2247<=int(x['frame'])<=2360]
    assert max(int(x['native_peak']) for x in roar('snes-roar'))>1000,'native roar did not survive music replacement'
    assert max(int(x['native_peak']) for x in roar('md-roar'))==0,'original roar leaked into MD source'
    assert (dest/'snes-roar.wav').read_bytes()!=(dest/'md-roar.wav').read_bytes(),'MD roar did not change audio'
    windows=[]
    for name in ('snes-hurt','md-hurt'):
        events=list(csv.DictReader((dest/(name+'-events.csv')).open()))
        hurt=next(x for x in events if x['event']=='0012' and x['actor']=='b213')
        start=int(hurt['frame']);following=next(int(x['frame']) for x in events if int(x['frame'])>start)
        windows.append((start+1,following))
    begin=max(x[0] for x in windows);end=min(x[1] for x in windows)
    assert end>begin,'hurt test did not isolate a native cue window'
    peak=lambda name:max(int(x['native_peak']) for x in results[name] if begin<=int(x['frame'])<=end)
    assert peak('snes-hurt')>1000,'native hurt cry did not play'
    assert peak('md-hurt')==0,'native hurt cry leaked into MD source'
    assert (dest/'snes-hurt.wav').read_bytes()!=(dest/'md-hurt.wav').read_bytes(),'MD hurt cry did not change audio'
    events=list(csv.DictReader((dest/'snes-hurt-events.csv').open()))
    lizard=[x for x in events if x['event']=='0014']
    cue=int(lizard[1]['frame'])
    next_cue=next(int(x['frame']) for x in events if int(x['frame'])>cue)
    native_peak=lambda name:max(int(x['native_peak']) for x in results[name] if cue+1<=int(x['frame'])<next_cue)
    assert native_peak('snes-hurt')>1000,'native lizard call did not play'
    assert native_peak('md-lizard')==0,'native lizard call leaked into MD source'
    assert (dest/'snes-hurt.wav').read_bytes()!=(dest/'md-lizard.wav').read_bytes(),'MD lizard call did not change audio'
    report={'result':'PASS','native_music_isolated':True,'native_fx_preserved':True,
            'md_roar_replaces_native_roar':True,'md_hurt_replaces_native_hurt':True,'md_lizard_replaces_native_call':True}
    (dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
