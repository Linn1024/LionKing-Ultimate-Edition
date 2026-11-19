"""Complete Pride with independent music and the existing MD resource mixture."""
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


def main():
    base=ROOT/'build/pride-music-output62';bp=base/'build-report.json';build=bound(bp)
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source)
    out=base/'completion';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name):
        folder=out/name;folder.mkdir();cmd=prior['commands']['aot'].copy();cmd[0]=str(base/'player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        if name=='snes-music':profile+='\naudio.music.pride_lands = snes\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name=='lle':cmd+=['--lle']
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv')),stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene=json.loads((folder/'scene.json').read_text());rows=list(csv.DictReader((folder/'driver.csv').open()))
        tracks=[int(r['value']) for r in rows if r['selector']=='1']
        checks[name+'_exit']=rc==0;checks[name+'_next_main_level']=scene['level']==1
        checks[name+'_music_choice_observed']=not tracks if name=='snes-music' else {137,134}<=set(tracks)
        observations[name]=dict(level=scene['level'],md_tracks=tracks)
        print(name,rc,observations[name],flush=True);return name,folder
    with ThreadPoolExecutor(max_workers=2) as pool:runs=dict(pool.map(run,('aot','lle','snes-music')))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    checks['all6000_compiled_interpreter_guest_fields']=len(hashes(runs['aot']))==6000 and hashes(runs['aot'])==hashes(runs['lle'])
    checks['all6000_music_source_guest_fields_independent']=hashes(runs['aot'])==hashes(runs['snes-music'])
    for file in ('audio.wav','window.png','scene.json','driver.csv'):checks[file+'_mode_parity']=digest(runs['aot']/file)==digest(runs['lle']/file)
    for file in ('window.png','scene.json'):checks[file+'_music_independent']=digest(runs['aot']/file)==digest(runs['snes-music']/file)
    checks['music_choice_changes_pcm']=digest(runs['aot']/'audio.wav')!=digest(runs['snes-music']/'audio.wav')
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                all_first_level_capabilities_not_claimed=True,public_preview_unchanged=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
