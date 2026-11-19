"""Check that an effect on the first input after loading is observed in both modes."""
import csv
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes

def main():
    state=ROOT/'build/windows-smoke/level.state';start=struct.unpack_from('<I',state.read_bytes(),12)[0]
    dest=ROOT/'build/pride-state-audio';dest.mkdir(parents=True,exist_ok=True)
    profile=dest/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.simba.roar = md\n')
    tape=dest/'first-roar.tape';tape.write_bytes(struct.pack('<64H',*([0x80]*4+[0]*60)))
    result={}
    for mode in ('aot','lle'):
        env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(dest/(mode+'-driver.csv'))
        env['TLK_AUDIO_EVENTS']=str(dest/(mode+'-events.csv'))
        command=[str(ROOT/'engine/build-win/tlk_sdl.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                 '--config',str(ROOT/'build/windows-smoke/host.ini'),'--load',str(state),
                 '--frames',str(start+64),'--input-polled',str(tape),'--no-pace','--no-audio','--no-record']
        if mode=='lle':command+=['--lle']
        log=dest/(mode+'.log')
        with log.open('wb') as output:
            subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=90)
        commands={(int(row['selector']),int(row['value'])) for row in csv.DictReader((dest/(mode+'-driver.csv')).open())}
        assert (19,10) in commands,mode+' missed the first roar after load'
        result[mode]=hashes(log);assert len(result[mode])==2
    assert result['aot']==result['lle'],'first-loaded-effect AOT/LLE state differs'
    (dest/'report.json').write_text(json.dumps({'result':'PASS','hashes':result},indent=2)+'\n')
    print('First loaded-frame MD effect AOT/LLE PASS',flush=True)

if __name__=='__main__':main()
