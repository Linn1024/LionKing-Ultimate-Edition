"""Verify independently selected leaf emission, gravity and one parent rustle.

The normal input prefix triggers original emitters. No guest actors, position,
health, RNG, map or instructions are changed by this verification tool.
"""
import csv
import hashlib
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-leaf-behavior';out.mkdir(parents=True,exist_ok=True)
    results={};tape=ROOT/'engine/tapes/allbugsF.read.tape'
    for name,behavior,audio,lle in [('native',False,False,False),('sound',False,True,False),
                                   ('behavior',True,False,False),('both',True,True,False),
                                   ('both-lle',True,True,True)]:
        folder=out/name;folder.mkdir(exist_ok=True)
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\n'+
            ('gameplay.levels.pride_lands.leaves = md\n' if behavior else '')+
            ('audio.effects.world.leaves = md\n' if audio else ''))
        env=os.environ.copy()
        for variable,file in [('TLK_LEAF_TRACE','leaves.csv'),('TLK_AUDIO_EVENTS','events.csv'),
                              ('TLK_MD_SOUND_COMMANDS','driver.csv'),('TLK_AUDIO_STEMS','stems.csv')]:
            env[variable]=str(folder/file)
        env['TLK_WRAM_DUMP']=','.join(map(str,range(1699,1721)));env['TLK_WRAM_DIR']=str(folder)
        cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
             '--config',str(ROOT/'build/windows-smoke/host.ini'),'--frames','1720',
             '--input-polled',str(tape),'--no-pace','--no-audio','--no-record',
             '--wav',str(folder/'output.wav'),'--wav-seconds','30',
             '--dump-window',str(folder/'window.png')]
        if lle:cmd.append('--lle')
        with (folder/'game.log').open('wb') as stream:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        dump=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
              '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
              '--frames','1720','--input-polled',str(tape)]
        if lle:dump.append('--lle')
        dump_env=env.copy()
        for variable in ('TLK_LEAF_TRACE','TLK_AUDIO_EVENTS','TLK_MD_SOUND_COMMANDS','TLK_AUDIO_STEMS'):dump_env.pop(variable,None)
        with (folder/'guest.log').open('wb') as stream:
            subprocess.run(dump,cwd=ROOT,env=dump_env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        # The headless host does not mix/advance the separate MD audio context
        # or publish its music-stop packet; full sound-driver WRAM may differ.
        assert hashes(folder/'guest.log')['frame_sha256']==hashes(folder/'game.log')['frame_sha256'],name+' SDL/headless picture differs'
        rows=list(csv.DictReader((folder/'leaves.csv').open()))
        triggers=[r for r in rows if r['event']=='trigger'];third=[r for r in rows if r['event']=='third_spawn_return']
        gravity=[r for r in rows if r['event']=='gravity']
        assert len(triggers)==1 and len(third)==int(behavior),(name,triggers,third)
        assert int((third or triggers)[0]['count'])==(3 if behavior else 2),(name,'wrong initial particle count')
        assert gravity and {int(r['value']) for r in gravity}=={0x1000 if behavior else 0x1800},(name,'wrong gravity')
        actors={int(r['actor'],16) for r in gravity}
        assert len(actors)==(3 if behavior else 2),(name,'wrong updated particle count',actors)
        integration=0
        for frame in range(1703,1721):
            prior=(folder/f'hl_wram_{frame-1}.bin').read_bytes();ram=(folder/f'hl_wram_{frame}.bin').read_bytes()
            for actor in actors:
                def velocity(data):return struct.unpack_from('<H',data,actor+0x3c)[0]|struct.unpack_from('<H',data,actor+0x3e)[0]<<16
                delta=(velocity(ram)-velocity(prior))&0xffffffff
                # A field boundary can split the actor walk; one actor can
                # receive two updates between adjacent end-of-field dumps.
                acceleration=0x1000 if behavior else 0x1800
                assert delta in (0,acceleration,acceleration*2),(name,frame,hex(actor),hex(delta))
                integration+=delta!=0
        assert integration>20,(name,'insufficient original particle integration')
        events=list(csv.DictReader((folder/'events.csv').open()))
        leaf_events=[r for r in events if int(r['event'],16)==0x17 and
                     ((int.from_bytes(bytes.fromhex(r['stack'])[5:8],'little')+1)&0xffffff)==0xc1fe7d]
        assert len(leaf_events)==len(actors),(name,'native leaf initialization callbacks missing')
        commands=list(csv.DictReader((folder/'driver.csv').open()))
        rustles=[r for r in commands if int(r['selector'])==2 and int(r['value'])==94]
        assert len(rustles)==int(audio),(name,'MD sound must be emitted once by parent',rustles)
        cue=max(int(r['frame']) for r in leaf_events)
        stems=list(csv.DictReader((folder/'stems.csv').open()))
        peak=max(int(r['native_peak']) for r in stems if cue+8<=int(r['frame'])<=1720)
        if audio:assert peak==0,(name,'Native leaf sound leaked',peak)
        results[name]={'hashes':hashes(folder/'game.log'),'particles':len(actors),'gravity':int(gravity[0]['value']),
                       'triggers':len(triggers),'native_child_callbacks':len(leaf_events),'md_rustles':len(rustles),
                       'integration_samples':integration,'native_peak':peak}
        print(name,'leaf count, original integration and independent parent sound PASS',flush=True)
    assert results['both']==results['both-lle'],'Leaf behavior/audio AOT/LLE mismatch'
    assert (out/'native/output.wav').read_bytes()!=(out/'sound/output.wav').read_bytes(),'Sound choice has no audible data effect'
    assert (out/'behavior/output.wav').read_bytes()!=(out/'both/output.wav').read_bytes(),'Sound source depends on behavior source'
    results['result']='PASS';(out/'report.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
