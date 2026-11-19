"""Observe actual original helper/constructor calls without changing guest state."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-porcupine-walk-calls-search';out.mkdir()
    source=ROOT/'build/pride-porcupine38/idle-roar-full/report.json';template=bound(source)['command']
    script=out/'observe.gdb'
    script.write_text('''set pagination off
set confirm off
break FN_C157E2_M0X0
commands
silent
printf "IDLE_HELPER frame=%u actor=%x strength=%u\\n", *(unsigned int*)&snes_frame_counter, *(unsigned short*)((char*)&g_ram+0x68), *(unsigned short*)((char*)&g_ram+0xa698)
bt 4
continue
end
break FN_C15791_M0X0
commands
silent
printf "LATE_CONSTRUCTOR frame=%u actor=%x strength=%u\\n", *(unsigned int*)&snes_frame_counter, *(unsigned short*)((char*)&g_ram+0x68), *(unsigned short*)((char*)&g_ram+0xa698)
bt 4
continue
end
run
''')
    tape=out/'neutral.poweron.tape'
    prior=ROOT/'build/pride-porcupine-idle-roar2/idle-roar2-16.poweron.tape'
    seed=bound(ROOT/'build/pride-porcupine38/idle-roar-seed2/report.json')
    poll=json.loads((ROOT/'build/pride-porcupine38/idle-roar-seed2/tree.jsonl').read_text().splitlines()[-1])['poll_index']
    tape.write_bytes(prior.read_bytes()[:poll*2]+bytes(800))
    template[template.index('--input-polled')+1]=str(tape)
    commands={};returns={}
    for label in ('normal','debugger'):
        folder=out/label;folder.mkdir();cmd=template.copy()
        for flag,value in [('--frames',3500),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if label=='debugger':cmd=['C:/mingw32/bin/gdb.exe','--batch','-x',str(script),'--args',*cmd]
        commands[label]=cmd
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        returns[label]=run.returncode;print(label,run.returncode,flush=True)
    text=(out/'debugger/run.log').read_text()
    checks=dict(normal_exit=returns['normal']==0,debugger_exit=returns['debugger']==0,
                walking_helper_called='FN_C150D7_M0X0' in text,
                no_roar_constructor='LATE_CONSTRUCTOR' not in text.split('Starting program:')[-1],
                actual_original_caller_chain='FN_C157E2_M0X0' in text and 'FN_C150D7_M0X0' in text,
                guest_hash_neutral=hashes(out/'normal/run.log')==hashes(out/'debugger/run.log'))
    for name in ('window.png','scene.json','audio.wav'):checks[name+'_neutral']=digest(out/'normal'/name)==digest(out/'debugger'/name)
    paths=[Path(__file__),source,Path(template[0]),script,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        debugger_operations=['break','read memory','backtrace','continue'],guest_register_or_memory_writes=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
