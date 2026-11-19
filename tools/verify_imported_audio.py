"""Verify imported MD audio needs neither the source filename nor cwd ROMs."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from audit_scenes import ROOT
from verify_pride_audio_state import wav_data
from verify_windows import hashes


def main():
    out=ROOT/'build/imported-audio';out.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'game-data/install.json').read_text())
    roms={name:ROOT/'game-data'/entry['file'] for name,entry in manifest['roms'].items()}
    before={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in roms.items()}
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.world.hyena_taunt = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    isolated=Path(tempfile.mkdtemp(prefix='empty-',dir=out))
    cases={'root':ROOT,'empty':isolated,'misleading-name':isolated}
    reference=None;results={}
    for name,cwd in cases.items():
        if name=='misleading-name':(isolated/'Lion King, The (World).md').write_bytes(b'Not the verified ROM')
        env=os.environ.copy();env['TLK_AUDIO_STEMS']=str(out/(name+'.csv'))
        command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(roms['snes']),'--md-rom',str(roms['megadrive']),
                 '--asset-cache',str(ROOT/'game-data/scenes-v1.cache'),'--resource-profile',str(profile),'--config',str(config),
                 '--load',str(ROOT/'build/pride-hyena-taunt/ready.state'),'--frames','4050',
                 '--input-polled',str(ROOT/'build/pride-hyena-taunt/after.polled.tape'),
                 '--no-pace','--no-audio','--no-record','--wav',str(out/(name+'.wav'))]
        log=out/(name+'.log')
        with log.open('wb') as stream:subprocess.run(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        text=log.read_text();assert 'MD audio ready' in text and 'resource_cache=loaded' in text
        rows=list(csv.DictReader((out/(name+'.csv')).open()));assert rows and max(int(row['md_peak']) for row in rows)>500
        result=(hashes(log),wav_data(out/(name+'.wav')))
        if reference is None:reference=result
        else:assert result==reference,(name,'Cwd or stray ROM changed verified imported playback')
        results[name]={'md_peak':max(int(row['md_peak']) for row in rows),'wav_sha256':hashlib.sha256(result[1]).hexdigest()}
    assert before=={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in roms.items()}
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'imported_data_unchanged':True,
        'no_original_filenames_required':True,'stray_rom_ignored':True,'cases':results},indent=2)+'\n')
    print('Imported audio exact from empty/stray-ROM working directories PASS',flush=True)


if __name__=='__main__':main()
