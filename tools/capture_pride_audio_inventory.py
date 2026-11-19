"""Inventory actual original MD sound calls through the first ordinary Pride exit.

Values sharing a number are not automatically equivalent semantic cues. This
read-only census identifies remaining callers for original-action comparison.
Run with .tools/python32/python.exe. No production behavior is changed.
"""
import argparse
from collections import Counter
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from md_lab import MdLab,png
from md_replay_movie import movie_inputs


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-audio-inventory')
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build');out.mkdir()
    original=ROOT/'tools/md_commands.c'
    source=original.read_text()
    needle='actor_valid?longword(actor+0x30)&0xffffff:0);'
    assert source.count(needle)==1
    source=source.replace(needle,'actor_valid?longword(actor+0x30)&0xffffff:0,word(0xccce));')
    needle='%06x,%06x,%04x,%06x\\n"'
    assert source.count(needle)==1
    source=source.replace(needle,'%06x,%06x,%04x,%06x,%u\\n"')
    needle='outer_caller,actor,actor_state\\n"'
    assert source.count(needle)==1
    source=source.replace(needle,'outer_caller,actor,actor_state,level\\n"')
    trace_source=out/'trace.c';trace_source.write_text(source)
    library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(trace_source),'-o',str(library)],check=True,cwd=ROOT)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    w=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
    index=0;ready=None;exit_field=None;exit_level=None
    try:
        for field in range(1,12001):
            trace.md_commands_frame(field);game.step(polled[index]);game.samples.clear()
            if trace.md_commands_polled():index+=1
            level=w(0xccce);camera=w(0xcd36)
            player=w(camera+0x24) if 0x8000<=camera<=0xff80 else 0
            if ready is None and level==1 and 0x8000<=player<=0xff80 and w(0xccf6)>0:
                ready=field;png(out/'ready.png',*game.image)
            if ready is not None and level!=1:
                exit_field=field;exit_level=level;png(out/'first-exit.png',*game.image);break
    finally:trace.md_commands_close();game.close()
    assert ready and exit_field,(ready,exit_field)
    rows=list(csv.DictReader((out/'commands.csv').open()))
    pride=[r for r in rows if ready<=int(r['frame'])<exit_field and r['level']=='1']
    groups=Counter((int(r['selector']),int(r['value']),r['outer_caller'],r['actor_state'])
        for r in pride if r['selector'] in ('2','19'))
    known_fm={94,97,98,101,105,112,116,117,123,124,165}
    known_pcm={1,3,4,7,10,15}
    inventory=[]
    for (selector,value,caller,state),count in sorted(groups.items()):
        matches=value in (known_fm if selector==2 else known_pcm)
        selected=[r for r in pride if int(r['selector'])==selector and int(r['value'])==value
            and r['outer_caller']==caller and r['actor_state']==state]
        inventory.append(dict(selector=selector,value=value,outer_caller=caller,actor_state=state,count=count,
            first_field=int(selected[0]['frame']),last_field=int(selected[-1]['frame']),
            value_has_an_existing_resource_mapping=matches,semantic_caller_equivalence_proven=False))
    paths=[Path(__file__),original,trace_source,library,movie,reference,ROOT/'tools/md_lab.py',
        ROOT/'tools/md_replay_movie.py',ROOT/'engine/runner/tlk_audio.c',
        ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='ORIGINAL_PRIDE_CENSUS_CAPTURED',ready_field=ready,first_exit_field=exit_field,
        first_exit_level_register=exit_level,ordinary_input_no_guest_edits=True,
        original_sound_call_groups=inventory,unknown_value_groups=[r for r in inventory if not r['value_has_an_existing_resource_mapping']],
        music_programs=sorted({int(r['value']) for r in pride if r['selector']=='1'}),
        all_first_level_audio_coverage_proven=False,production_mappings_unchanged=True,
        rom_sha256=hashlib.sha256(rom).hexdigest(),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(inventory),'sound/caller groups;',len(report['unknown_value_groups']),
        'groups without an existing numeric mapping; first exit',exit_field,exit_level,flush=True)


if __name__=='__main__':main()
