"""Current native control and independently selected entrance-window AOT/LLE play."""
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
    base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';build=bound(bp)
    reference=ROOT/'build/pride-hyena-probe103/fights104/report.json';ref=bound(reference);assert ref['result']=='PASS'
    out=base/'fights140';out.mkdir();checks={};commands={};counts={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda p:re.findall(pattern,p.read_text())
    for name in ('native','entrance-aot','entrance-lle'):
        folder=out/name;folder.mkdir();cmd=ref['commands']['native'].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            if flag=='--resource-profile':text+='\ngameplay.levels.pride_lands.hyena_entrance_window = '+('snes' if name=='native' else 'md')+'\n'
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name.endswith('lle'):cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_HYENA_ENTRANCE_TRACE=str(folder/'entrance.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        rows=list(csv.DictReader((folder/'entrance.csv').open())) if (folder/'entrance.csv').exists() else []
        counts[name]=len(rows);commands[name]=cmd
        checks[name+'_exit_and4320_fields']=rc==0 and len(hashes(folder/'run.log'))==4320
        checks[name+'_scoped_operand']=not rows if name=='native' else bool(rows) and all(int(r['selected_operand'])==int(r['camera_x'])+64 and int(r['timer'])>0 for r in rows)
        print(name,'exit',rc,'adjustments',len(rows),flush=True)
    control=out/'native';a=out/'entrance-aot';b=out/'entrance-lle'
    checks['native_all4320_original_guest_fields_preserved']=hashes(control/'run.log')==hashes(reference.parent/'native/run.log')
    checks['native_whole_pcm_preserved']=digest(control/'audio.wav')==digest(reference.parent/'native/audio.wav')
    checks['selected_all4320_guest_mode_parity']=hashes(a/'run.log')==hashes(b/'run.log')
    checks['selected_choice_changes_actual_gameplay']=hashes(a/'run.log')!=hashes(control/'run.log')
    for file in ('window.png','scene.json','audio.wav','entrance.csv'):checks[file+'_selected_mode_parity']=digest(a/file)==digest(b/file)
    checks['current_binary_bound']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,reference,ROOT/'engine/runner/tlk_hyena_entrance.c',ROOT/'engine/cmake/final-frontend-patches/hyena-entrance-window.hunks']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,adjustment_counts=counts,
        scope='Ordinary Normal fight from power-on, root SNES with only entrance-window leaf changed. Native all4320 canonical guest fields and whole PCM preserved; selected actual callback operands/positive timers and full guest/media mode parity. Headless, not a whole original-MD trajectory, UI/source-switch or final-level completion proof.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,counts,flush=True)
if __name__=='__main__':main()
