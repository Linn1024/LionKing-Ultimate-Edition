"""Check encounter-effect selection independently of music on the Difficult tape."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output65';bp=base/'build-report.json';bound(bp)
    observer=base/'allbugs-observer2';op=observer/'build-report.json';observed=bound(op)
    source=ROOT/'build/pride-hyena-mixtures58/report.json';prior=bound(source)
    out=base/'hyena-effects';out.mkdir();checks={};commands={};observations={};folders={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    for name in ('native','effects-aot','effects-lle'):
        folder=out/name;folder.mkdir();cmd=prior['commands']['hard-art-aot'].copy();cmd[0]=str(observer/'player.exe')
        cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,4601)))
        path=Path(cmd[cmd.index('--resource-profile')+1]);profile=path.read_text()
        if name!='native':
            selected=Path(prior['commands']['hard-mixed-aot'][prior['commands']['hard-mixed-aot'].index('--resource-profile')+1]).read_text()
            profile='\n'.join(line for line in selected.splitlines() if not line.startswith('audio.music.'))+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--resource-profile','resources.ini'),('--config','host.ini'),('--wav','audio.wav'),('--dump-window','window.png'),('--dump-scene','scene.json')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name.endswith('lle'):cmd+=['--lle']
        commands[name]=cmd
        env=dict(clean,TLK_TRACKED_RAM_LOG=str(folder/'route.ram'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene=json.loads((folder/'scene.json').read_text());guest=scene['latched_gameplay']
        owned=any(p['actor_descriptor']==0xc58c68 and p['actor_owner']==p['object'] and p['actor_action']==0xc147f7 for p in scene['pieces'])
        checks[name+'_exit']=rc==0;checks[name+'_alive_victory']=guest['health']>0 and owned
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        checks[name+'_no_md_music']=not any(r['selector']=='1' for r in driver)
        checks[name+'_effect_choice_observed']=bool(driver) if name!='native' else not driver
        observations[name]=dict(health=guest['health'],lives=guest['lives'],owned_boss_death=owned,md_commands=len(driver))
        folders[name]=folder;print(name,rc,observations[name],flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def pictures(folder):return [(r[0],r[1]) for r in re.findall(pattern,(folder/'run.log').read_text())]
    for name in ('effects-aot','effects-lle'):
        checks[name+'_all4600_canonical_pictures_native']=len(pictures(folders[name]))==4600 and pictures(folders[name])==pictures(folders['native'])
        actual=(folders[name]/'route.ram').read_bytes().splitlines();reference=(folders['native']/'route.ram').read_bytes().splitlines()
        checks[name+'_all4600_tracked_gameplay_fields_native']=len(actual)==4600 and actual==reference
        checks[name+'_selected_effects_change_pcm']=digest(folders[name]/'audio.wav')!=digest(folders['native']/'audio.wav')
    checks['selected_whole_pcm_mode_parity']=digest(folders['effects-aot']/'audio.wav')==digest(folders['effects-lle']/'audio.wav')
    checks['observer_exact']=digest(observer/'player.exe')==observed['binary_sha256']
    paths=[Path(__file__),bp,op,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                limited_to_encounter_effect_mixture=True,native_sound_transport_wram_not_expected_equal=True,
                all_effects_or_all_encounter_histories_not_claimed=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
