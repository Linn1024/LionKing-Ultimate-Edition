"""Check live port spawn bounds against the untouched original MD grid routine.

The grid oracle uses controlled camera coordinates in an isolated research core;
it does not prove gameplay, enemy lifetime or initialization order equivalence.
Long chase captures explicitly retain their still-unresolved contact differences.
Run with the32-bit research Python.
"""
import ctypes as C
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from audit_scenes import read_rom


def main():
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    source=ROOT/'build/pride-roll-grid-fixed/snes.json';capture=json.loads(source.read_text())
    assert capture['ordinary_native_input_boot'] and capture['md_camera_selected'] and capture['md_start_selected']
    assert source.stat().st_mtime>=(ROOT/'dist/LionKing.exe').stat().st_mtime,'Recapture on the current host'
    out=ROOT/'build/pride-spawn-grid';out.mkdir(exist_ok=True)
    raw=(ROOT/'build/pride-roll-contacts/ready-md.state').read_bytes();assert b'TLKAE001' in raw
    game=MdLab();state=C.create_string_buffer(raw)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(raw))
    def w(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    def put(at,v):game.work_ram[at]=v&255;game.work_ram[at+1]=(v>>8)&255
    camera=w(0xcd36);assert [w(at) for at in (0xcd1c,0xcd1e,0xcd20)]==[28,200,80]
    # Call the original function; no ROM instructions are copied or patched.
    game.write_code(0xfe00,bytes.fromhex('4eb90009270a60fe'))
    coordinates=sorted({(r['camera_words'][4],r['camera_words'][5]+1) for rows in capture['cases'].values() for r in rows})
    oracle={}
    try:
        for x,y in coordinates:
            put(camera+8,x);put(camera+10,y)
            for reg,value in ((8,0xff0000|camera),(9,0xffe930),(17,0x2700),(15,0xfffd00),(16,0xfffe00)):
                game.core.m68k_set_reg(reg,value)
            game.step();oracle[(x,y)]=[w(at) for at in (0xe930,0xe932,0xe934,0xe936)]
    finally:game.close()
    fields=0
    for name,rows in capture['cases'].items():
        for index,row in enumerate(rows):
            xy=(row['camera_words'][4],row['camera_words'][5]+1)
            assert row['spawn_bounds']==oracle[xy],(name,index,'original MD spawn bounds',row['spawn_bounds'],oracle[xy])
            fields+=1
    original=json.loads((ROOT/'build/pride-roll-contacts/md.json').read_text())
    first=capture['cases']['long-roll-chase'][0]['spawn_bounds']
    before_path=ROOT/'build/pride-roll-contacts-ordinary/long-roll-chase/snes/hl_wram_2457.bin'
    old=None
    if before_path.exists():
        before=before_path.read_bytes();old=[struct.unpack_from('<H',before,at)[0] for at in (0xb1ff,0xb201,0xb203,0xb205)]
        assert old==[929,1279,65521,415]
    assert first==original['cases']['long-roll-chase'][0]['spawn_bounds']==[945,1279,65521,415]
    report={'result':'PASS','scope':__doc__,'original_function':0x9270a,
            'native_raster_y_plus_one_used_for_md_grid':True,'actual_native_fields_checked':fields,
            'unique_original_cpu_fixtures':len(coordinates),'old_initial_bounds':old,'corrected_initial_bounds':first,
            'fixture_rows':[{'camera':list(xy),'original_bounds':bounds} for xy,bounds in oracle.items()],
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'headless_sha256':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest(),
            'long_contact_protocols_or_initialization_equivalence_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD grid routine matches',fields,'live port fields across',len(coordinates),'camera fixtures PASS',flush=True)


if __name__=='__main__':main()
