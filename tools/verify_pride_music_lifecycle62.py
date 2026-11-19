"""Fresh death/revival, final life and Continue music mixtures on candidate62."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-music-output62';bp=base/'build-report.json';build=bound(bp)
    template_source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';template=bound(template_source)['commands']['aot']
    out=base/'lifecycle';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    leaves={'native':[], 'level':['pride_lands'], 'death':['pride_health_death'],
            'both':['pride_lands','pride_health_death'], 'over':['pride_game_over'],
            'all':['pride_lands','pride_health_death','pride_game_over']}
    tapes={'revival':ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape',
           'hard':ROOT/'build/pride-game-over-music/hard.tape', 'continue':ROOT/'build/pride-game-over-music/normal.tape'}
    ends={'revival':5400,'hard':3000,'continue':5300};saves={'revival':4500,'hard':2850,'continue':4450}
    def run(item):
        route,profile,mode=item;name=f'{route}-{profile}-{mode}';folder=out/name;folder.mkdir()
        cmd=template.copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--frames')+1]=str(ends[route])
        index=cmd.index('--input-polled');cmd[index]='--input-polled' if route=='revival' else '--input';cmd[index+1]=str(tapes[route])
        cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,ends[route]+1)))
        (folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+''.join('audio.music.'+key+' = md\n' for key in leaves[profile]))
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        save=mode=='aot' and profile==('both' if route=='revival' else 'all')
        if save:cmd+=['--save-at',str(saves[route]),str(folder/'current.state')]
        if mode=='lle':cmd+=['--lle']
        commands[name]=cmd
        env=dict(clean,TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        if save:env['TLK_SOFT_TREE_LOG']=str(folder/'tree.jsonl')
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0
        rows=list(csv.DictReader((folder/'driver.csv').open()));tracks=[int(r['value']) for r in rows if r['selector']=='1']
        guest=json.loads((folder/'scene.json').read_text())['latched_gameplay']
        if route=='revival':
            expected={'native':[],'level':[137,137,134,0,137],'death':[430,0],'both':[137,137,134,430,137]}[profile]
            checks[name+'_independent_music_commands']=tracks==expected
            checks[name+'_revived_in_pride']=guest['descriptor']==0x387 and guest['health']>0
        else:
            checks[name+'_gameover_music_choice']=(327 in tracks)==(profile in ('over','all'))
            if route=='hard':
                checks[name+'_no_nonfinal_death_track']=430 not in tracks
                checks[name+'_actual_gameover']=guest['descriptor']==0x57b and guest['health']==guest['lives']==0
            else:
                checks[name+'_continue_restores_level']=guest['descriptor']==0x387 and guest['health']==4 and guest['lives']==2 and guest['player']==[64,1255]
                checks[name+'_two_nonfinal_death_tracks']=tracks.count(430)==(2 if profile=='all' else 0)
            if profile=='over':checks[name+'_over_only_commands']=tracks==([327] if route=='hard' else [327,0])
        observations[name]=dict(tracks=tracks,guest=guest)
        print(name,'exit',rc,'tracks',tracks,flush=True);return name,folder
    cases=[(route,profile,mode) for route in tapes for profile in (('native','level','death','both') if route=='revival' else ('native','over','all')) for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool:runs=dict(pool.map(run,cases))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    for route,profile,mode in cases:
        name=f'{route}-{profile}-{mode}';folder=runs[name];native=runs[f'{route}-native-aot']
        checks[name+'_all_guest_fields_equal_native']=len(hashes(folder))==ends[route] and hashes(folder)==hashes(native)
        checks[name+'_scene_equal_native']=digest(folder/'scene.json')==digest(native/'scene.json')
        if mode=='lle':checks[route+'_'+profile+'_whole_pcm_mode_parity']=digest(folder/'audio.wav')==digest(runs[f'{route}-{profile}-aot']/'audio.wav')
    for route in tapes:
        profile='both' if route=='revival' else 'all';full=runs[f'{route}-{profile}-aot'];folder=out/(route+'-loaded');folder.mkdir()
        cmd=commands[f'{route}-{profile}-aot'].copy();i=cmd.index('--save-at');del cmd[i:i+3];cmd+=['--load',str(full/'current.state')]
        if route=='revival':
            row=next(json.loads(line) for line in (full/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==saves[route])
            tail=folder/'remaining.polled.tape';tail.write_bytes(tapes[route].read_bytes()[row['poll_index']*2:]);cmd[cmd.index('--input-polled')+1]=str(tail)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[route+'-loaded']=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[route+'_current_resume_exit']=rc==0
        checks[route+'_every_resumed_guest_field_exact']=hashes(folder)==[r for r in hashes(full) if int(r[0])>saves[route]]
        whole=wav_data(full/'audio.wav');tail=wav_data(folder/'audio.wav')
        checks[route+'_resumed_pcm_suffix_exact']=bool(tail) and whole[-len(tail):]==tail
        checks[route+'_resumed_scene_exact']=digest(folder/'scene.json')==digest(full/'scene.json')
        print(route,'current resume',rc,flush=True)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,template_source,*tapes.values()]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                fresh_input_only_complete_runs=len(cases),current_build_resumes_only=True,public_preview_unchanged=True,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
