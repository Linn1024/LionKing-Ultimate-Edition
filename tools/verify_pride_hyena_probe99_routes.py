"""Native preservation and both independently selected probe routes to level1."""
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
    base=ROOT/'build/pride-hyena-probe97';bp=base/'build-report.json';build=bound(bp)
    reference=ROOT/'build/pride-menu-enable86/route/report.json';prior=bound(reference);assert prior['result']=='PASS'
    out=base/'routes99';out.mkdir();checks={};commands={};observations={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for name in ('native','probe-aot','probe-lle'):
        folder=out/name;folder.mkdir();cmd=prior['commands']['menus-aot'].copy();cmd[0]=str(base/'player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        profile+='\ngameplay.levels.pride_lands.hyena_probe_height = '+('snes' if name=='native' else 'md')+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name.endswith('lle'):cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_HYENA_PROBE_TRACE=str(folder/'probes.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene=json.loads((folder/'scene.json').read_text());rows=list(csv.DictReader((folder/'probes.csv').open())) if (folder/'probes.csv').exists() else []
        checks[name+'_full_route_to_next_level']=rc==0 and scene['level']==1 and len(hashes(folder))==6000
        checks[name+'_scoped_probe_behavior']=not rows if name=='native' else bool(rows) and all(int(r['selected_query_y'])==(int(r['native_query_y'])-8)&65535 for r in rows)
        observations[name]=dict(level=scene['level'],probe_count=len(rows));commands[name]=cmd
        print(name,'exit',rc,'level',scene['level'],'probes',len(rows),flush=True)
    a=out/'probe-aot';b=out/'probe-lle';control=out/'native'
    checks['native_all6000_pictures_and_full_wram_preserved']=hashes(control)==hashes(reference.parent/'menus-aot')
    checks['native_whole_pcm_preserved']=digest(control/'audio.wav')==digest(reference.parent/'menus-aot/audio.wav')
    checks['selected_all6000_guest_mode_parity']=hashes(a)==hashes(b)
    for file in ('window.png','scene.json','audio.wav','probes.csv'):
        checks[file+'_selected_mode_parity']=digest(a/file)==digest(b/file)
    checks['new_leaf_compiled_available']='-DTLK_HYENA_PROBE_AVAILABLE=1' in build['compiles']['resources']
    paths=[Path(__file__),bp,reference]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='Ordinary completed mixed route with native or MD walking-probe choice. Headless; real window/UI and natural slope interactions remain separate.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
