"""Native control plus current selected LLE fight, paired with actual103 MD AOT."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-probe103';out=base/'fights104';out.mkdir()
bp=base/'build-report.json';bound(bp)
mdpath=ROOT/'build/pride-hyena-probe103-fight/report.json';md=bound(mdpath);assert md['result']=='CAPTURED'
old=ROOT/'build/pride-hyena-probe102-fight/report.json';bound(old)
contexts=list(csv.DictReader((old.parent/'contexts.csv').open()))
expected=[(int(r['field']),r['pc'],r['actor'],int(r['a']),int(r['a'])-8) for r in contexts if r['action']=='c13c83' and r['caller'] in ('c14070','c1408b')]
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
def probes(folder):return [(int(r['field']),r['pc'],r['actor'],int(r['native_query_y']),int(r['selected_query_y'])) for r in csv.DictReader((folder/'probes.csv').open())]
checks={'all177_actual_scoped_original_calls_reproduced':len(expected)==177 and probes(mdpath.parent)==expected};commands={}
for name in ('native','probe-lle'):
    folder=out/name;folder.mkdir();cmd=md['command'].copy()
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        text=Path(cmd[cmd.index(flag)+1]).read_text()
        if name=='native':text=text.replace('hyena_probe_height = md','hyena_probe_height = snes')
        (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    if name.endswith('lle'):cmd+=['--lle']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_HYENA_PROBE_TRACE=str(folder/'probes.csv'))
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    checks[name+'_exit']=rc==0;commands[name]=cmd;print(name,'exit',rc,flush=True)
control=out/'native';selected=out/'probe-lle'
checks['native_all_recorded_guest_fields_preserved']=hashes(control)==hashes(old.parent)
checks['native_no_selected_probe']=not (control/'probes.csv').exists()
checks['selected_all_guest_fields_mode_parity']=hashes(selected)==hashes(mdpath.parent)
checks['selected_actual177_probes_mode_parity']=probes(selected)==expected
for file in ('window.png','scene.json','audio.wav'):checks[file+'_selected_mode_parity']=digest(selected/file)==digest(mdpath.parent/file)
checks['native_whole_pcm_preserved']=digest(control/'audio.wav')==digest(old.parent/'audio.wav')
paths=[Path(__file__),bp,mdpath,old]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Ordinary original Normal repeated-hit fight, root SNES graphics/audio/terrain with only new probe choice changed. Native guest/PCM preserved and selected AOT/LLE fields/media/probes equal. Slope decision reproduction separately proven in original slice.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
