"""Verify ordinary boss saves, source guards and cold cross-build continuations."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-rng-player4';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    previous=ROOT/'build/pride-rng-player3';out=base/'boss-saves';out.mkdir()
    profile=ROOT/'build/pride-rng-player2/completion-reference-unpaused256/256/resources.ini'
    tape=previous/'width-arena-input/route.polled.tape';neutral=out/'neutral.polled.tape';neutral.write_bytes(bytes(4096))
    wrong=out/'wrong-rng.ini';wrong.write_text(profile.read_text()+'\ngameplay.levels.pride_lands.random_entry = snes\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};checks={}
    def run(label,binary,mode,load=None,save=False,bad=False):
        folder=out/label;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',wrong if bad else profile,'--config',config,'--input-polled',neutral if load else tape,
             '--frames',3000,'--no-pace','--no-audio','--no-record',
             '--hash-at',','.join(map(str,range(2801 if load else 1,3001))),
             '--wav',folder/'audio.wav','--wav-seconds',120,'--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        if mode=='lle':cmd+=['--lle']
        if load:cmd+=['--load',load]
        if save:cmd+=['--save-at',2800,folder/'boss.state']
        commands[label]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(commands[label],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        return result.returncode
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for mode in ('aot','lle'):
        checks[mode+'/old_uninterrupted_exit']=run('old-'+mode,previous/'player.exe',mode)==0
        checks[mode+'/new_save_exit']=run('new-'+mode,base/'player.exe',mode,save=True)==0
        old,new=out/('old-'+mode),out/('new-'+mode)
        checks[mode+'/save_all_fields_neutral']=len(rows(new))==3000 and rows(new)==rows(old)
        checks[mode+'/save_whole_pcm_neutral']=wav_data(new/'audio.wav')==wav_data(old/'audio.wav')
        checks[mode+'/save_whole_client_neutral']=pixels(new/'window.png')==pixels(old/'window.png')
        state=new/'boss.state';record=state.read_bytes();before=digest(state)
        checks[mode+'/private_boss_envelope']=record[:8]==b'PRPRAC01' and int.from_bytes(record[20:24],'little')==2800
        expected=[r for r in rows(new) if int(r[0])>2800]
        for generation,binary in (('new',base/'player.exe'),('old',previous/'player.exe')):
            label=f'{generation}-resume-{mode}'
            checks[label+'/exit']=run(label,binary,mode,load=state)==0
            resumed=out/label;checks[label+'/every_field']=len(rows(resumed))==200 and rows(resumed)==expected
            pcm=wav_data(resumed/'audio.wav');checks[label+'/entire_pcm']=bool(pcm) and pcm==wav_data(new/'audio.wav')[-len(pcm):]
            checks[label+'/whole_client']=pixels(resumed/'window.png')==pixels(new/'window.png')
        checks[mode+'/wrong_source_rejected']=run('wrong-'+mode,base/'player.exe',mode,load=state,bad=True)==8 and 'State scene-random source differs' in (out/('wrong-'+mode)/'run.log').read_text()
        checks[mode+'/original_save_preserved']=digest(state)==before
        print(mode,[k for k,v in checks.items() if not v],flush=True)
    checks['every_aot_lle_field']=rows(out/'new-aot')==rows(out/'new-lle')
    checks['whole_aot_lle_pcm']=wav_data(out/'new-aot/audio.wav')==wav_data(out/'new-lle/audio.wav')
    checks['whole_aot_lle_client']=pixels(out/'new-aot/window.png')==pixels(out/'new-lle/window.png')
    for mode in ('aot','lle'):
        scene=json.loads((out/('new-'+mode)/'scene.json').read_text())
        checks[mode+'/actual_boss_scene']=scene['level']==0 and scene['latched_gameplay']['descriptor']==0x80d
    paths=[Path(__file__),bp,previous/'build-report.json',profile,tape,previous/'width-arena-input/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,compared_fields=6800,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
