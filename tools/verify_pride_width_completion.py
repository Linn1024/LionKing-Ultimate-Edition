"""Verify ordinary narrow-view supported-mixture completion in both player modes."""
import csv
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
    author=base/'width-fight1/report.json';planning=bound(author)
    assert planning['uninterrupted_full_wram_matches_planning'] and not planning['loaded_states_in_final_replay']
    tape=base/'width-fight1/best.polled.tape';assert digest(tape)==planning['selected_tape_sha256']
    profile=ROOT/'build/pride-rng-player2/completion-reference-unpaused256/256/resources.ini'
    end=base/'width-fight-cold-end/report.json';cold=bound(end)
    assert cold['observations']['level']==1 and cold['observations']['first_next_level_field']==3450
    assert not cold['observations']['life_loss_fields']
    out=base/'width-completion';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        env=dict(clean,TLK_SPRITE_REPORT=str(folder/'coverage.json'),TLK_SPRITE_OBJECTS=str(folder/'pride-objects.csv'),
                 TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),
                 TLK_RNG_ENTRY_TRACE=str(folder/'entry.csv'))
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',4500,
             '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,4501))),
             '--wav',folder/'route.wav','--wav-seconds',120,'--dump-scene',folder/'scene.json',
             '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        if mode=='lle':cmd+=['--lle']
        commands[mode]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[mode],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        checks[mode+'/exit']=r.returncode==0
        rows=re.findall(pattern,(folder/'run.log').read_text())
        checks[mode+'/all_fields_recorded']=len(rows)==4500
        scene=json.loads((folder/'scene.json').read_text());coverage=json.loads((folder/'coverage.json').read_text())
        checks[mode+'/next_main_level']=scene['level']==1
        objects=list(csv.DictReader((folder/'pride-objects.csv').open()))
        pride_missing=[pose for pose in coverage['missing_poses'] if any(int(row['pose'],16)&0x3fffff==pose for row in objects)]
        checks[mode+'/all_observed_pride_art_mapped']=not pride_missing and not coverage['missing_npc_poses']
        tracks={int(row['value']) for row in csv.DictReader((folder/'driver.csv').open()) if row['selector']=='1'}
        checks[mode+'/pride_and_boss_tracks']={137,134}<=tracks
        stems=list(csv.DictReader((folder/'stems.csv').open()))
        checks[mode+'/md_audio_rendered']=len(stems)>1000 and max(int(row['md_peak']) for row in stems)>500
        entry=list(csv.DictReader((folder/'entry.csv').open()))
        checks[mode+'/only_normal_entry_reseed']=len(entry)==1 and entry[0]['selected']=='aa0b4c'
        width,height,_=pixels(folder/'window.png');checks[mode+'/actual_native_width']=(width,height)==(512,448)
        observations[mode]=dict(final_level=scene['level'],global_native_fallback_poses=coverage['missing_poses'],
            observed_pride_missing_poses=pride_missing,entry=entry,tracks=sorted(tracks))
        print(mode,[k for k,v in checks.items() if not v],flush=True)
    a,b=out/'aot',out/'lle'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['every_aot_lle_field']=rows(a)==rows(b)
    checks['whole_aot_lle_pcm']=wav_data(a/'route.wav')==wav_data(b/'route.wav')
    checks['whole_aot_lle_client']=pixels(a/'window.png')==pixels(b/'window.png')
    checks['whole_aot_lle_guest']=pixels(a/'guest.png')==pixels(b/'guest.png')
    checks['mode_coverage_equal']=json.loads((a/'coverage.json').read_text())==json.loads((b/'coverage.json').read_text())
    paths=[Path(__file__),bp,author,tape,profile,end]
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,observations=observations,commands=commands,
        compared_fields=4500,first_next_level_field=3450,normal_rng_on_256_completion_verified=True,
        ordinary_poweron_controller_inputs_only=True,loaded_states=False,practice_or_guest_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())


if __name__=='__main__':main()
