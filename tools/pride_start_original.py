"""Observe the original Pride default-position loaders without actor edits.

MD uses an ordinary Start-button boot and an observational CPU hook. Native
uses original interpreter execution, with no MD ROM or selected resources.
"""
import argparse
import csv
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',choices=('md','native','compare'))
    args=parser.parse_args()
    out=ROOT/'build/pride-start-original';out.mkdir(parents=True,exist_ok=True)
    if args.source=='md':
        import ctypes as C
        from md_lab import MdLab,png
        read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
        game=MdLab();trace=C.CDLL(str(ROOT/'build/md_start_trace.dll'))
        trace.md_start_trace_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.md_start_trace_init(game.core._handle,str(out/'md.csv').encode())
        try:
            for frame in range(1800):
                trace.md_start_trace_frame(frame+1)
                game.step((1<<3) if 200<frame<1500 and frame%90<3 else 0)
            png(out/'md-ready.png',*game.image)
        finally:trace.md_start_trace_close();game.close()
        rows=list(csv.DictReader((out/'md.csv').open()))
        assert len(rows)==1 and rows[0]['source']=='1' and rows[0]['record']=='1cfdb4'
        assert rows[0]['x']=='65' and rows[0]['y']=='1255' and rows[0]['level']=='1'
        assert rows[0]['checkpoint_x']==rows[0]['checkpoint_y']=='0'
        report={'result':'PASS','scope':__doc__,'source':'original MD, ordinary boot, no guest edits',
                'loader_pc':0x1d017a,'record':0x1cfdb4,'field_offset':36,'loads':rows}
    elif args.source=='native':
        read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
        profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
        env=os.environ.copy();env['TLK_START_TRACE']=str(out/'native.csv')
        command=[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                 '--resource-profile',profile,'--lle','--frames',1400,
                 '--input-polled',ROOT/'engine/tapes/allbugsF.read.tape']
        with (out/'native.log').open('wb') as log:
            subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        rows=[r for r in csv.DictReader((out/'native.csv').open()) if r['pc'] in ('c0867d','c08689')]
        assert len(rows)==2 and [r['native'] for r in rows]==['64','1248']
        assert all(r['source_md']==r['changed']==r['checkpoint']=='0' and r['native']==r['selected'] for r in rows)
        report={'result':'PASS','scope':__doc__,'source':'original native LLE, ordinary input, no MD ROM/choices',
                'record':0x387,'field_offsets':[22,24],'loads':rows}
    else:
        native=json.loads((out/'native.json').read_text());md=json.loads((out/'md.json').read_text())
        assert native['result']==md['result']=='PASS'
        s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
        m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
        a=list(struct.unpack_from('<2H',s,0x387+22));b=list(struct.unpack_from('>2H',m,0x1cfdb4+36))
        assert a==[64,1248] and b==[65,1255]
        assert s[0x867b:0x867d]==s[0x8687:0x8689]==s[0x7763:0x7765]==bytes.fromhex('b7df')
        assert m[0x1d6e72:0x1d6e76]==bytes.fromhex('20ac0024')
        assert m[0x1d017a:0x1d017c]==bytes.fromhex('209c')
        report={'result':'PASS','scope':__doc__,'native_initial_xy':a,'md_initial_xy':b,
                'native_default_x_comparison_pc':0xc07763,'native_checkpoint_flag_address':0x1ffa2,
                'native_checkpoint_restore_branch':0xc08693,'md_checkpoint_restore_branch':0x1d6e78,
                'normal_default_loads_observed_both_originals':True,'checkpoint_positions_not_replaced_by_this_mapping':True,
                'source_report_sha256':{k:hashlib.sha256((out/(k+'.json')).read_bytes()).hexdigest() for k in ('native','md')}}
    path=out/(args.source+'.json');path.write_text(json.dumps(report,indent=2)+'\n')
    print(args.source,'original Pride default-position evidence PASS',flush=True)


if __name__=='__main__':main()
