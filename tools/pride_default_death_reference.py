"""Find an ordinary original MD health death before reaching the checkpoint."""
import csv
import ctypes as C
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-default-death-reference';out.mkdir(exist_ok=True)
    path=out/'report.json';path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    source=ROOT/'build/md-next-levels-replay';inputs=json.loads((source/'frames.json').read_text())
    trace=C.CDLL(str(ROOT/'build/md_revival_trace.dll'))
    trace.md_revival_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    trace.md_revival_trace_last_return.restype=C.c_uint
    trials=[]
    for prefix in (1500,1600,1400,2500,3500):
        folder=out/str(prefix);folder.mkdir(exist_ok=True)
        game=MdLab();assert trace.md_revival_trace_init(game.core._handle,str(folder/'callbacks.csv').encode())
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        word=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
        death=None;rows=[];checks=0;previous=0;resumed=None
        try:
            for frame in range(1,prefix+4501):
                trace.md_revival_trace_frame(frame);game.step(inputs[frame-1]['pad'] if frame<=prefix else 0)
                if frame<=prefix and frame%100==1:
                    control=source/f'{frame:05d}-wram.bin'
                    if control.exists():assert bytes(game.work_ram)==control.read_bytes();checks+=1
                health=word(0xccf6)
                if frame>prefix and not health and previous and word(0xccce)==1:death=frame
                if death:
                    actor=word(0xcd48);draw=word(actor+12)
                    rows.append({'frame':frame,'health':health,'lives':word(0xccee),'checkpoint':word(0xccd6)<<16|word(0xccd8),
                                 'xy':[word(actor+8),word(actor+10)],'camera':[word(0x880c),word(0x880e)],
                                 'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                                 'words':[word(actor+i*2) for i in range(64)],'cram':bytes(game.cram).hex()})
                    if rows[-1]['checkpoint'] or word(0xe956)==65535:break
                    resumed=trace.md_revival_trace_last_return()
                    if resumed>death:
                        png(folder/'revived.png',*game.image);break
                previous=health;game.samples.clear()
        finally:trace.md_revival_trace_close();game.close()
        events=list(csv.DictReader((folder/'callbacks.csv').open()))
        entries=[r for r in events if r['pc']=='1d6cb2' and death and int(r['frame'])>=death]
        valid=death and resumed and resumed>death and entries and not int(entries[0]['checkpoint'],16) and not int(entries[0]['skip'],16)
        trials.append({'prefix_fields':prefix,'death':death,'resumed':resumed,'valid_health_death':bool(valid),'unchanged_prefix_wram':checks})
        if not valid:continue
        selected=[r for r in events if death<=int(r['frame'])<=resumed]
        (folder/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
        unique=lambda pc:[int(r['frame']) for r in selected if r['pc']==pc]
        case={'death':death,'checkpoint':0,'health_restored':next(r['frame'] for r in rows if r['health']),
              'main_loop_start':unique('1d6d9c'),'main_loop_end':unique('1d6e00'),
              'complete_fade_end':unique('1d6e22'),'new_actor_owner':unique('1d6e4c'),
              'fade_in_call':unique('1d70f6'),'fade_in_return':unique('1d70fc'),
              'respawn_hold_iterations':len(unique('1d7158')),'normal_play_jump':unique('1d71ce')}
        report={'result':'PASS','scope':__doc__,'trials':trials,'case':case,'selected_prefix_fields':prefix,
                'loaded_states':False,'guest_edits':False,'source_sha256':{'script':digest(Path(__file__)),
                'trace_source':digest(ROOT/'tools/md_revival_trace.c'),'trace_dll':digest(ROOT/'build/md_revival_trace.dll'),
                'core':digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),'input':digest(source/'frames.json'),
                'fields':digest(folder/'fields.json'),'callbacks':digest(folder/'callbacks.csv')}}
        path.write_text(json.dumps(report,indent=2)+'\n');print('Original pre-checkpoint health-death/revival PASS',json.dumps(case),flush=True);return
    path.write_text(json.dumps({'result':'NO_HEALTH_DEATH_ROUTE','trials':trials},indent=2)+'\n')
    raise AssertionError(trials)


if __name__=='__main__':main()
