"""Trace complete original MD fatal hurt initialization and same-field dispatch."""
import csv
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png


def main():
    out=ROOT/'build/pride-fatal-entry';out.mkdir()
    source=ROOT/'tools/md_fatal_entry_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    tape=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(tape.read_text())
    trace=C.CDLL(str(library));trace.md_fatal_entry_init.argtypes=[C.c_void_p,C.c_char_p]
    cases={};checks={};paths=[Path(__file__),source,tape,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    for name,prefix,death in (('default',1400,2902),('checkpoint',4000,4755)):
        folder=out/name;folder.mkdir();game=MdLab()
        assert trace.md_fatal_entry_init(game.core._handle,str(folder/'events.csv').encode())
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        prefix_checks=0
        try:
            for field in range(1,death+3):
                trace.md_fatal_entry_field(field);game.step(inputs[field-1]['pad'] if field<=prefix else 0);game.samples.clear()
                if field<=prefix and field%100==1:
                    control=ROOT/f'build/md-next-levels-replay/{field:05d}-wram.bin'
                    if control.exists():assert bytes(game.work_ram)==control.read_bytes();prefix_checks+=1;paths.append(control)
                if field in (death-1,death,death+1,death+2):
                    (folder/f'wram-{field}.bin').write_bytes(bytes(game.work_ram));png(folder/f'field-{field}.png',*game.image)
        finally:trace.md_fatal_entry_close();game.close()
        rows=list(csv.DictReader((folder/'events.csv').open()))
        selected=[r for r in rows if int(r['field'])==death]
        checks[name+'/fatal_call_and_complete_return_before_dispatch']=[r['event'] for r in selected]==[
            'hit_select','fatal_hurt_entry','fatal_hurt_return','death_dispatch']
        checks[name+'/selected_body_executes_at_zero']=selected[1]['health']==selected[2]['health']==selected[3]['health']=='0'
        checks[name+'/directional_hurt_initialized']=selected[2]['action'] in ('196b4c','196d04') and selected[2]['timer']=='18' and selected[2]['vy']=='fffd0000'
        checks[name+'/same_field_dispatch_retains_actor_state']=selected[2]['actor_words']==selected[3]['actor_words']
        checks[name+'/natural_prefix_controls']=prefix_checks==prefix//100
        cases[name]=dict(prefix=prefix,death=death,events=selected,prefix_wram_controls=prefix_checks)
        print(name,'complete original fatal body/dispatch',selected,flush=True)
    report=dict(result='ORIGINAL_FATAL_ENTRY_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
        ordinary_power_on_inputs=True,loaded_states=False,guest_writes_added=False,
        first_display_effect_of_hurt_initialization_proven=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
