"""Replay the complete first level with the packaged Pride Lands preset."""
import json
import hashlib
import csv
import os
import subprocess
import wave
from audit_scenes import ROOT
from verify_windows import hashes
from pride_start_route import prepare

def main():
    dest=ROOT/'build/pride-mix-verification';dest.mkdir(parents=True,exist_ok=True)
    baseline=json.loads((ROOT/'build/pride-baseline/report.json').read_text())['hashes']
    profile=(ROOT/'profiles/pride-lands.ini').read_text()
    config=dest/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    results={}
    adapted=prepare(ROOT/'engine/tapes/allbugsF.read.tape',dest/'md-start.polled.tape')
    for name,frames in [('graphics',5000),('mixed',5000),('hyena',3890)]:
        tape=ROOT/'engine/tapes/allbugsF.read.tape' if name=='graphics' else adapted
        if name!='graphics':frames+=3
        choices=profile if name!='graphics' else '\n'.join(x for x in profile.splitlines() if not x.startswith(('audio.','gameplay.')))+'\n'
        source=dest/(name+'.ini');source.write_text(choices)
        env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(dest/(name+'-coverage.json'))
        env['TLK_MD_SOUND_COMMANDS']=str(dest/(name+'-driver.csv'))
        env['TLK_BG_TRACE']=str(dest/(name+'-background.csv'))
        cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
             '--resource-profile',str(source),'--frames',str(frames),'--input-polled',str(tape),
             '--no-pace','--no-audio','--no-record','--dump-window',str(dest/(name+'.png')),
             '--dump-scene',str(dest/(name+'.json'))]
        if name=='mixed':cmd+=['--wav',str(dest/'mixed.wav'),'--wav-seconds','90']
        log=dest/(name+'.log')
        with log.open('wb') as output:subprocess.run(cmd,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=120)
        scene=json.loads((dest/(name+'.json')).read_text());coverage=json.loads((dest/(name+'-coverage.json')).read_text())
        assert not coverage['missing_poses'] and not coverage['missing_npc_poses'],name+' had unmapped observed cub/enemy art'
        assert scene['level']==(0 if name=='hyena' else 1),name+' did not reach the expected level'
        if name=='graphics':assert hashes(log)==baseline,'combined graphics changed the guest state'
        else:
            commands=list(csv.DictReader((dest/(name+'-driver.csv')).open()))
            tracks=[int(x['value']) for x in commands if x['selector']=='1']
            assert 137 in tracks and 134 in tracks,name+' did not switch to the MD hyena battle track'
            effects={(int(x['selector']),int(x['value'])) for x in commands}
            assert (19,15) in effects and (2,101) in effects,name+' missed the bonus bug or checkpoint cue'
        previous=None;phase_checks=0;lag_checks=0
        for row in csv.DictReader((dest/(name+'-background.csv')).open()):
            valid=row['stage']=='1' and row['level']=='0' and int(row['descriptor']) in (0x387,0x80d)
            if not valid:previous=None;continue
            camera=[int(row['md_camera_x']),int(row['md_camera_y'])]
            if previous is not None:
                if row['advanced']=='1':
                    assert camera==[int(previous['raster_x']),int(previous['raster_y'])],name+' background lost the original MD camera phase'
                    phase_checks+=1
                else:
                    assert camera==[int(previous['md_camera_x']),int(previous['md_camera_y'])],name+' background advanced on a repeated frame'
                    lag_checks+=1
            previous=row
        assert phase_checks>100,name+' did not cover moving background updates'
        results[name]={'end_level':scene['level'],'coverage':coverage,'hashes':hashes(log),
                       'frames':frames,'controller_tape_sha256':hashlib.sha256(tape.read_bytes()).hexdigest()}
        results[name]['background_phase_checks']=phase_checks;results[name]['background_lag_checks']=lag_checks
        print(name,'PASS',flush=True)
    with wave.open(str(dest/'mixed.wav'),'rb') as audio:
        assert audio.getframerate()==48000 and audio.getnchannels()==2 and audio.getnframes()>70*48000
    report={'result':'PASS','graphics_guest_state_unchanged':True,'complete_mixed_first_level_route':True,'runs':results}
    (dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Complete supported first-level mix route PASS')

if __name__=='__main__':main()
