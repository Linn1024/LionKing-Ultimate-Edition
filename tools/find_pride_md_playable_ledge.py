"""Find a playable opposite ledge by branching only ordinary original inputs."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs


def main():
    out=ROOT/'build/pride-ledge-controlled/find-playable';out.mkdir(parents=True)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv';pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();library=ROOT/'build/pride-cub-contact-audio/trace.dll';trace=C.CDLL(str(library))
    trace.md_contact_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_contact_audio_init(game.core._handle,str(out/'entries.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    game.core.retro_serialize_size.restype=C.c_size_t;size=game.core.retro_serialize_size()
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    def state():
        buf=C.create_string_buffer(size);assert game.core.retro_serialize(buf,size)
        assert b'TLKAE001' in buf.raw
        return buf.raw
    def sample(field):
        a=word(word(0xcd36)+0x24)
        return dict(field=field,actor=a,x=word(a+8),y=word(a+10),
            action=f'{word(a+0x30)<<16|word(a+0x32):06x}',
            level=word(0xccce),poll=int(bool(trace.md_contact_audio_polled())))
    candidates=[];index=0;trials=[];found=None
    try:
        for field in range(1,2601):
            trace.md_contact_audio_field(field);game.step(polled[index]);game.samples.clear()
            if trace.md_contact_audio_polled():index+=1
            row=sample(field)
            if field%2==0 and row['actor']==0x93ce and 1090<=row['x']<=1255 and 310<=row['y']<=510:
                candidates.append((row,state(),index))
        print('Natural candidate checkpoints',len(candidates),flush=True)
        # Input words are libretro directions/buttons, not guest memory edits.
        patterns={
            'neutral':[0]*100,'left':[1<<6]*100,'right':[1<<7]*100,
            'brake-4':[1<<6]*4+[0]*96,'brake-8':[1<<6]*8+[0]*92,
            'brake-12':[1<<6]*12+[0]*88,
            'wait-8-right':[0]*8+[1<<7]*92,
            'wait-16-right':[0]*16+[1<<7]*84,
            'right-8-left':[1<<7]*8+[1<<6]*92,
        }
        for start,raw,used in candidates:
            for name,inputs in patterns.items():
                buf=C.create_string_buffer(raw);assert game.core.retro_unserialize(buf,len(raw))
                event=None
                for n,pad in enumerate(inputs):
                    field=start['field']+n+1;trace.md_contact_audio_field(field);game.step(pad);game.samples.clear()
                    row=sample(field)
                    if row['action']=='194da6' and row['actor']==0x93ce and row['poll'] and row['level']==1:
                        event=row;break
                trials.append(dict(start=start,pattern=name,entry=event))
                if event and (event['x'],event['y'])==(1232,481):
                    found=dict(start=start,pattern=name,inputs=inputs[:n+1],entry=event,route_polls_before_branch=used)
                    (out/'branch.state').write_bytes(raw);(out/'ledge.state').write_bytes(state())
                    (out/'checkpoint-wram.bin').write_bytes(bytes(game.work_ram));png(out/'checkpoint.png',*game.image)
                    print('Found',found,flush=True);break
            if found:break
    finally:trace.md_contact_audio_close();game.close()
    paths=[Path(__file__),movie,reference,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='FOUND' if found else 'NOT_FOUND',found=found,trials=trials,
        guest_mutations=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(trials),'ordinary input trials',flush=True)


if __name__=='__main__':main()
