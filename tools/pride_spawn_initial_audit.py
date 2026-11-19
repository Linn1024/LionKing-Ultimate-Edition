"""Observe initial spawn ordering and original MD ground-lizard lifecycle.

Ordinary controller boot, observational CPU hooks only. This records a difference
and does not claim initialization or enemy behavior equivalence.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',choices=('md','native','compare'))
    source=parser.parse_args().source;out=ROOT/'build/pride-spawn-initial';out.mkdir(exist_ok=True)
    if source=='md':
        import ctypes as C
        from md_lab import MdLab
        read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
        game=MdLab();trace=C.CDLL(str(ROOT/'build/md_spawn_trace.dll'))
        trace.md_spawn_trace_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.md_spawn_trace_init(game.core._handle,str(out/'original-md.csv').encode())
        try:
            for frame in range(1800):
                trace.md_spawn_trace_frame(frame+1);game.step(8 if 200<frame<1500 and frame%90<3 else 0)
        finally:trace.md_spawn_trace_close();game.close()
        rows=list(csv.DictReader((out/'original-md.csv').open()))
        scans=[r for r in rows if r['pc']=='09270a']
        births=[r for r in rows if r['pc']=='18d414' and r['marker']=='14' and r['argument_x']=='352' and r['argument_y']=='1248']
        removed=[r for r in rows if r['pc']=='0928e0']
        assert scans[0]['x']=='0' and scans[0]['y']=='1056' and scans[0]['level']=='1'
        assert len(births)==len(removed)==1 and births[0]['frame']=='1288' and removed[0]['x']=='416' and removed[0]['y']=='1261'
        report={'result':'PASS','scope':__doc__,'source':'Original MD ordinary-input boot, no guest edits',
                'first_spawn_scan':scans[0],'ground_lizard_birth':births[0],'ground_lizard_out_of_bounds':removed[0]}
    elif source=='native':
        read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
        profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.camera = md\ndisplay.viewport = md\ngameplay.levels.pride_lands.start = md\n')
        raw=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes();words=struct.unpack('<'+'H'*(len(raw)//2),raw)
        tape=out/'ordinary-boot.polled.tape';tape.write_bytes(raw[:words.index(0x100)*2])
        env=os.environ.copy();env['TLK_SPAWN_WINDOW_TRACE']=str(out/'initial.csv')
        cmd=[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--lle','--frames',1100,'--input-polled',tape]
        with (out/'game.log').open('wb') as log:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        rows=[r for r in csv.DictReader((out/'initial.csv').open()) if r['level']=='0' and r['descriptor']=='903']
        first=next(r for r in rows if r['caller']=='b8c5')
        assert first['camera_x']==first['camera_y']=='0' and first['cached_lead']=='32' and first['camera_active']=='1'
        assert not any(r['cached_lead']=='0' for r in rows),'Re-evaluate cached-lead hypothesis'
        report={'result':'PASS','scope':__doc__,'source':'Port original LLE, only MD start/camera320 selected, ordinary input',
                'first_spawn_scan':first,'spawn_observations':len(rows),'cached_lead_missing_during_pride':False,
                'headless_sha256':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest()}
    else:
        native=json.loads((out/'native.json').read_text());md=json.loads((out/'md.json').read_text())
        assert native['result']==md['result']=='PASS'
        assert native['first_spawn_scan']['camera_y']=='0' and md['first_spawn_scan']['y']=='1056'
        report={'result':'DIFFERENCE','scope':__doc__,'native_initial_scan_camera_y':0,'md_initial_scan_camera_y':1056,
                'native_initial_scan_caller':0xc086d9,'native_camera_seek_loop':[0xc0874b,0xc08798],
                'md_first_spawn_field':1288,'md_first_ground_lizard_xy':[352,1248],
                'md_ground_lizard_out_of_bounds_xy':[416,1261],
                'initialization_order_equivalent':False,'cached_lead_hypothesis_rejected':True,
                'cause_of_all_long_contact_differences_proven':False}
    (out/(source+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(source,'spawn initialization evidence:',report['result'],flush=True)


if __name__=='__main__':main()
