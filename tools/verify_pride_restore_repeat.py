"""Require byte-exact same-host replay of the canonical restore/idle policy."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-scene-restore-repeat';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    base=ROOT/'build/pride-scene-restore-sdl';primary=base/'report.json';reference=json.loads(primary.read_text())
    assert reference['result']=='RESTORE_AND_HANDOFF_VERIFIED_RENDER_PLAYER_OPEN'
    binary=ROOT/'engine/build-win/tlk_scene_restore_sdl.exe';assert digest(binary)==reference['probe_sha256']
    results={}
    for source in ('native','both'):
        original=base/(source+'-canonical');folder=out/source;folder.mkdir(exist_ok=True)
        for name,sha in reference['runs'][source+'-canonical']['artifacts_sha256'].items():assert sha==digest(original/name)
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--config',base/'host.ini',
            '--lle','--frames','5400','--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
            '--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100',
            '--dump-window',folder/'window.png','--dump-png',folder/'picture.png']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        assert hashes(folder/'run.log')==hashes(original/'run.log'),source
        pcm=wav_data(folder/'route.wav');assert pcm==wav_data(original/'route.wav'),source
        assert pixels(folder/'window.png')==pixels(original/'window.png'),source
        assert (folder/'owner-fields.csv').read_bytes()==(original/'owner-fields.csv').read_bytes(),source
        assert (folder/'restore-events.csv').read_bytes()==(original/'restore-events.csv').read_bytes(),source
        results[source]={'exact_pcm_bytes':len(pcm),'exact_guest_window_and_scene_fields':True,
            'artifacts_sha256':{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}}
        print(source,'canonical restore new-process replay exact WAV/guest/window/scene fields PASS',flush=True)
    assert digest(binary)==reference['probe_sha256']
    report.write_text(json.dumps({'result':'PASS','scope':__doc__,'runs':results,'probe_sha256':digest(binary),
        'production_behavior_enabled':False,'native_song_phase_equivalence_verified':False,
        'source_sha256':{'script':digest(Path(__file__)),'primary_report':digest(primary),
            'restore_coordinator':digest(ROOT/'tools/pride_scene_restore_probe.c')}},indent=2)+'\n')


if __name__=='__main__':main()
