"""Try ordinary leftward approaches from the genuine original-MD Sun encounter."""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    observed=ROOT/'build/md-continue-token-original2/report.json';assert bound(observed)['result']=='PASS'
    qualified=observed.parent/'qualification/report.json';assert bound(qualified)['result']=='PASS'
    out=ROOT/'build/md-continue-token-contact';out.mkdir();game=MdLab()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2';pads,_,settings=movie_inputs(movie)
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    with reference.open() as f:polled=[pads[int(r['frame'])-1] for r in csv.DictReader(f) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    library=qualified.parent/'trace.dll';trace=C.CDLL(str(library));trace.pickup_flight_init.argtypes=[C.c_void_p,C.c_char_p]
    trace.pickup_flight_observe.argtypes=[C.c_int]
    assert trace.pickup_flight_init(game.core._handle,str(out/'seed-calls.csv').encode());trace.pickup_flight_observe(0)
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
    index=0;cases=[];checks={}
    try:
        for field in range(1,2744):
            trace.pickup_flight_field(field);game.step(polled[index])
            if trace.pickup_flight_polled():index+=1
        trace.pickup_flight_close();seed_ram=bytes(game.work_ram)
        prior_fields=[json.loads(r) for r in (qualified.parent/'sun-observer/fields.jsonl').read_text().splitlines()]
        checks['genuine_seed_matches_qualified_original']=hashlib.sha256(seed_ram).hexdigest()==prior_fields[2742]['wram']
        size=game.core.retro_serialize_size();state=C.create_string_buffer(size);assert game.core.retro_serialize(state,size)
        (out/'seed.state').write_bytes(state.raw);(out/'seed-ram.bin').write_bytes(seed_ram);png(out/'seed.png',*game.image)
        base_credits=word(0xccda)
        for left_fields in range(0,81,5):
            folder=out/f'left-{left_fields}';folder.mkdir();assert game.core.retro_unserialize(state,size)
            game.samples.clear();assert trace.pickup_flight_init(game.core._handle,str(folder/'calls.csv').encode());trace.pickup_flight_observe(1)
            try:
                for step in range(1,151):
                    trace.pickup_flight_field(2743+step);game.step(1<<6 if step<=left_fields else 0)
                rows=list(csv.DictReader([])) if False else None
            finally:trace.pickup_flight_close()
            rows=list(csv.DictReader((folder/'calls.csv').open()))
            cues=[r for r in rows if r['callback'] in ('18fd7c','18fdb6')]
            result=dict(left_fields=left_fields,credits_before=base_credits,credits_after=word(0xccda),cues=cues)
            cases.append(result)
            if cues:
                png(folder/'final.png',*game.image);(folder/'audio.pcm').write_bytes(game.samples)
                print('CONTACT',result,flush=True);break
        checks['actual_pickup_contact_found']=any(c['cues'] for c in cases)
        checks['early_level_music15_branch']=any(any(r['callback']=='18fd7c' for r in c['cues']) and c['credits_after']==c['credits_before']+1 for c in cases)
    finally:trace.pickup_flight_close();game.close()
    paths=[Path(__file__),observed,qualified,library,movie,reference]
    report=dict(result='PASS' if all(checks.values()) else 'SEARCH_INCOMPLETE',checks=checks,cases=cases,input_polls_to_seed=index,
                ordinary_input_from_genuine_state=True,no_guest_register_or_memory_edits=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
