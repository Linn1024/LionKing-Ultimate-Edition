"""Observe original MD health death and revival using only controller inputs.

The retained unforced movie prefix ends at4000; all later input is neutral.
The hyena removes health, the original game loses one life and restores the
checkpoint. No loaded state, actor/world/RNG or ROM edits are used.
Run with embedded32-bit Python and the existing observational commands DLL.
"""
import csv
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def main():
    out=ROOT/'build/pride-health-death-original';out.mkdir(exist_ok=True)
    path=out/'report.json';path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    source=ROOT/'build/md-next-levels-replay/frames.json';rows=json.loads(source.read_text())
    game=MdLab();trace=C.CDLL(str(ROOT/'build/md_commands.dll'))
    trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    word=lambda a:struct.unpack_from('<H',bytes(game.work_ram),a)[0]
    death=None;revival=None;checks=0;records=[];milestones=[];life_loss=None;previous_lives=None
    try:
        for frame in range(1,5401):
            trace.md_commands_frame(frame);game.step(rows[frame-1]['pad'] if frame<=4000 else 0)
            health=word(0xccf6);camera=word(0xcd36);player=word(camera+36) if 0x8000<=camera<=0xff80 else 0
            lives=word(0xccee)
            if frame>=4000:
                if previous_lives is not None and lives<previous_lives and life_loss is None:life_loss=frame
                previous_lives=lives
            if frame>4000 and word(0xccce)==1:
                if health==0 and death is None:death=frame
                if death and health>0 and revival is None:revival=frame
                if frame%16==0 or frame in (death,revival):
                    records.append({'frame':frame,'health':health,'xy':[word(player+8),word(player+10)] if player else None,
                                    'player_state':(word(player+48)<<16|word(player+50))&0xffffff if player else None})
            if frame<=4000 and frame%100==1:
                expected=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                if expected.exists():assert bytes(game.work_ram)==expected.read_bytes();checks+=1
            if frame in (4000,4800,5400):
                milestones.append({'frame':frame,'health':health,'lives':word(0xccee),
                                   'xy':[word(player+8),word(player+10)],
                                   'checkpoint':[word(0xccd6),word(0xccd8)]})
                png(out/f'{frame}.png',*game.image)
                (out/f'{frame}-wram.bin').write_bytes(bytes(game.work_ram))
            game.samples.clear()
    finally:trace.md_commands_close();game.close()
    commands=list(csv.DictReader((out/'commands.csv').open()))
    music=[r for r in commands if r['selector']=='1' and int(r['frame'])>=4000]
    assert death==4755 and revival==5025,(death,revival)
    assert [(int(r['frame']),int(r['value']),r['caller']) for r in music]==[(4755,430,'1d6ce0'),(5100,137,'1d71c6')],music
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    assert rom[0x1d6cc8:0x1d6cce]==bytes.fromhex('203c000001ae')
    assert [r['lives'] for r in milestones]==[9,8,8]
    assert milestones[-1]['health']==6 and milestones[-1]['xy']==[1200,111]
    assert all(r['checkpoint']==[1200,112] for r in milestones)
    (out/'life-report.json').write_text(json.dumps({'result':'PASS','scope':'Original MD life loss/checkpoint restoration on the same controller-only route',
        'milestones':milestones,'death_frame':death,'life_loss_frame':life_loss,'health_restored_frame':revival,
        'one_life_lost':True,'checkpoint_restored':True},indent=2)+'\n')
    report={'result':'PASS','scope':__doc__,'death_frame':death,'revival_health_frame':revival,
            'original_death_music':430,'original_level_music_after_revival':137,'music_calls':music,
            'unchanged_original_prefix_wram_snapshots':checks,'ordinary_power_on':True,'loaded_states':False,
            'source_sha256':{'input':hashlib.sha256(source.read_bytes()).hexdigest(),
                            'rom':hashlib.sha256(rom).hexdigest(),
                            'commands':hashlib.sha256((out/'commands.csv').read_bytes()).hexdigest()},
            'fall_death_or_game_over_verified':False}
    (out/'samples.json').write_text(json.dumps(records,indent=2)+'\n');path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original health-death430 and revived-level137 music; ordinary input only PASS',flush=True)


if __name__=='__main__':main()
