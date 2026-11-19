"""Verify independently selected death artwork with MD music and cross-source saves."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-owned-death-audio';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    reference=ROOT/'build/pride-health-death-music/both-aot'
    baseline=wav_data(reference/'route.wav');guest=hashes(reference/'run.log')
    assert json.loads((reference.parent/'report.json').read_text())['result']=='PASS'
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    zero=out/'neutral.polled.tape';zero.write_bytes(bytes(12000))
    profiles={}
    for name,frames,palette in [('native-art','snes','md'),('md-art','md','snes')]:
        path=out/(name+'.ini');path.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'
            'audio.music.pride_lands = md\naudio.music.pride_health_death = md\n'
            f'graphics.sprites.simba.cub.frames = {frames}\ngraphics.sprites.simba.cub.palette = {palette}\n')
        profiles[name]=path
    state=out/'playing.state'
    poses={int(r['snes'],16) for r in json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())['cub_death_frames']}

    def run(name,profile,mode='aot',load=False,save=False):
        folder=out/name;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(folder/'coverage.json')
        cmd=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profiles[profile],
            '--config',config,'--frames','5400','--input-polled',zero if load else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
            '--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100',
            '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        if mode=='lle':cmd+=['--lle']
        if save:cmd+=['--save-at','4500',state]
        if load:cmd+=['--load',state]
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        return folder

    runs=[]
    for profile in profiles:
        pictures=[]
        for mode in ('aot','lle'):
            folder=run(profile+'-'+mode,profile,mode,save=profile=='native-art' and mode=='aot')
            assert wav_data(folder/'route.wav')==baseline and hashes(folder/'run.log')==guest,(profile,mode)
            coverage=json.loads((folder/'coverage.json').read_text())
            seen=set(coverage['seen_owned_native_death_poses']) if profile=='native-art' else {r['snes'] for r in coverage['seen_cub_poses']}
            assert poses<=seen,(profile,mode,'Missing selected-source death poses')
            pictures.append(pixels(folder/'window.png'))
            runs.append({'profile':profile,'mode':mode,'all_twenty_selected_source_poses':True,'exact_reference_audio_and_guest':True})
        assert pictures[0]==pictures[1]
        print(profile,'all20 selected poses with MD music, exact AOT/LLE/reference audio and guest PASS',flush=True)
    continuations=[]
    for profile in profiles:
        folder=run('loaded-'+profile,profile,load=True)
        audio=wav_data(folder/'route.wav')
        assert audio and audio==baseline[-len(audio):]
        assert hashes(folder/'run.log')==guest
        assert pixels(folder/'window.png')==pixels(out/(profile+'-aot')/'window.png')
        continuations.append({'profile':profile,'exact_audio_bytes':len(audio),'exact_picture_and_guest':True})
        print(profile,'new-process mixed-audio graphics-compatible save continuation PASS',flush=True)
    result={'result':'PASS','scope':__doc__,'player_sha256':digest(ROOT/'dist/LionKing.exe'),
        'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),'ordinary_runs':runs,
        'graphics_changed_continuations':continuations,'source_sha256':{'script':digest(Path(__file__)),
            'music_report':digest(reference.parent/'report.json'),'reference_wav':digest(reference/'route.wav'),
            'renderer':digest(ROOT/'engine/runner/tlk_wide.c'),'sprites':digest(ROOT/'engine/runner/tlk_md_sprites.c')},
        'death_gameplay_source_enabled':False}
    report.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
