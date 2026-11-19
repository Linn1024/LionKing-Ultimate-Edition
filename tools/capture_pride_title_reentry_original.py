"""Observe original caption creation across natural default/checkpoint deaths."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from md_lab import MdLab,png
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-title-reentry-original';out.mkdir()
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text())
    library=ROOT/'build/pride-title-original2/trace.dll';trace=C.CDLL(str(library))
    trace.title_init.argtypes=[C.c_void_p,C.c_char_p]
    checks={};cases={}
    for name,prefix,death in [('default',1400,2902),('checkpoint',4000,4755)]:
        folder=out/name;folder.mkdir();game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        assert trace.title_init(game.core._handle,str(folder/'calls.csv').encode())
        def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
        first_death=None;previous_health=None;restored=False;captures=[]
        try:
            for field in range(1,death+501):
                trace.title_field(field);game.step(inputs[field-1]['pad'] if field<=prefix else 0);game.samples.clear()
                health=word(0xccf6)
                if field>prefix and previous_health and not health and first_death is None:first_death=field
                if field>death and health:restored=True
                previous_health=health
                if field not in (death-1,death+270,death+300,death+350,death+420):continue
                png(folder/f'{field}.png',*game.image)
                captures.append(dict(field=field,health=health,lives=word(0xccee),level=word(0xccce)))
        finally:trace.title_close();game.close()
        calls=list(csv.DictReader((folder/'calls.csv').open()))
        checks[name+'/actual_fatal_entry']=first_death==death
        checks[name+'/revival_observed']=restored
        checks[name+'/initial_caption_only']=len(calls)==100 and all(int(r['field'])<death and r['level']=='1' for r in calls)
        cases[name]=dict(prefix=prefix,death=death,captures=captures,caption_calls=len(calls),
                        caption_after_death=sum(int(r['field'])>=death for r in calls))
        print(name,cases[name],flush=True)
    paths=[Path(__file__),source,library,ROOT/'tools/md_title_trace.c',ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                original_pride_caption_not_recreated_by_these_health_revives=True,
                ordinary_inputs_no_guest_edits=True,continue_gameover_not_verified=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'original caption/revival checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
