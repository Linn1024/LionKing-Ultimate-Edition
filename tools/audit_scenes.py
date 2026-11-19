"""Capture native SNES layer evidence and inventory MD scene descriptors.

Standard library only. Run after scripts/Build.ps1. Generated data stays in build/.
The inventory distinguishes decoded assets from verified layer/scroll behavior.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NAMES=['Pride Lands',"Can't Wait to Be King",'Elephant Graveyard','Stampede',
       "Simba's Exile",'Hakuna Matata',"Simba's Destiny",'Be Prepared',
       "Simba's Return",'Pride Rock','Bug Toss','Bug Hunt 1','Bug Hunt 2','Bug Hunt 3']
SCROLL={0x8ba88:'uniform_xy',0x8bb28:'horizontal_bands',0x8bf34:'horizontal_bands',
        0x8c26e:'horizontal_bands',0x8db82:'half_x_and_scroll_table',
        0x8dfda:'horizontal_bands',0x8e77c:'half_x_fixed_y',
        0x8e7e8:'horizontal_bands',0x8e2b0:'horizontal_bands',0x8c252:'fixed'}

def read_rom(name,expected):
    data=(ROOT/name).read_bytes()
    if hashlib.sha256(data).hexdigest()!=expected: raise ValueError('unsupported ROM: '+name)
    return data

def compress_lines(lines):
    bands=[]
    for line in lines:
        properties={k:v for k,v in line.items() if k!='y'}
        if bands and bands[-1]['registers']==properties: bands[-1]['end']=line['y']+1
        else: bands.append({'start':line['y'],'end':line['y']+1,'registers':properties})
    return bands

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--frames',type=int,default=2300)
    ap.add_argument('--reuse',action='store_true',help='analyze existing captures without launching the player')
    ap.add_argument('--levels',type=int,nargs='+',default=list(range(14)),help='only recapture these levels; retain existing others')
    ap.add_argument('--replay-frame',type=int,help='capture one selected level through the All Bugs replay instead of level select')
    args=ap.parse_args()
    if args.replay_frame is not None and len(args.levels)!=1: ap.error('--replay-frame requires one --levels entry')
    target_frame=args.replay_frame if args.replay_frame is not None else args.frames
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    spec=importlib.util.spec_from_file_location('tlk_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec); spec.loader.exec_module(lz)
    dest=ROOT/'build/scene-audit'; dest.mkdir(parents=True,exist_ok=True)
    config=dest/'host.ini'; config.write_text('opengl = 1\nscale = 1\n')
    profiles={}
    for source,choices in [('snes',''),('mixed','graphics.scenery = md\ndisplay.viewport = md\n')]:
        path=dest/(source+'.ini'); path.write_text('schema = 1\ngame = snes\n'+choices); profiles[source]=path
    rows=[]
    for level,name in enumerate(NAMES):
        stem=f'{level:02d}'
        if not args.reuse and level in args.levels:
            for source in profiles:
                cmd=[str(ROOT/'engine/build-win/tlk_sdl.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                     '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
                     '--resource-profile',str(profiles[source]),
                     '--frames',str(target_frame),'--no-pace','--no-audio','--no-record',
                     '--dump-window',str(dest/(stem+'-'+source+'.png'))]
                if args.replay_frame is None: cmd+=['--practice-level',str(level)]
                else: cmd+=['--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape')]
                if source=='snes': cmd+=['--dump-scene',str(dest/(stem+'.json'))]
                with (dest/(stem+'-'+source+'.log')).open('wb') as log:
                    subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
            capture=json.loads((dest/(stem+'.json')).read_text())
            capture['host_frame']=target_frame
            capture['capture_method']='allbugs_replay' if args.replay_frame is not None else 'practice_level_select'
            (dest/(stem+'.json')).write_text(json.dumps(capture)+'\n')
        capture=json.loads((dest/(stem+'.json')).read_text()) if (dest/(stem+'.json')).exists() else None
        rec=0x1cfdb4+level*48
        descriptor=struct.unpack_from('>I',md,rec+32)[0]
        update,initialize=struct.unpack_from('>II',md,descriptor)
        bgptr,palette=struct.unpack_from('>I',md,rec+24)[0],struct.unpack_from('>I',md,rec+44)[0]
        bg,_=lz.decompress(md,bgptr)
        layers=[]
        matched=capture is not None and capture['level']==level
        paired_hashes=[]
        for source in profiles:
            log=dest/(stem+'-'+source+'.log')
            paired_hashes.append(dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',log.read_text(),re.M)) if log.exists() else {})
        guest_equal=len(paired_hashes[0])==2 and paired_hashes[0]==paired_hashes[1]
        if matched and not guest_equal: raise RuntimeError(f'paired captures changed guest state for level {level}')
        for i,layer in enumerate(capture['layers'] if matched else []):
            scrolls={tuple(line['scroll'][i]) for line in capture['lines'] if not line['blank'] and (line['main']|line['sub'])&(1<<i)}
            layers.append({**layer,'distinct_scroll_pairs':len(scrolls)})
        status='captured' if matched else 'wrong_level' if capture else 'missing'
        if matched and not any(x['enabled_lines'] for x in layers): status='backgrounds_disabled_in_sample'
        row={'level':level,'name':name,'sample_frame':capture.get('host_frame',2300) if capture else None,'snes':{
            'capture_status':status,'actual_level':capture['level'] if capture else None,
            'paired_guest_hashes_equal':guest_equal,
            'camera':capture['camera'] if matched else None,'stage_detected':capture['stage_detected'] if matched else None,
            'modes':sorted({l['mode'] for l in capture['lines']}) if matched else [], 'layers':layers,
            'register_bands':compress_lines(capture['lines']) if matched else []},'md':{
            'descriptor':hex(rec),'background_asset':hex(bgptr),'background_bytes':len(bg),
            'background_map_size':[512,len(bg)//128*8],
            'update':hex(update),'initialize':hex(initialize),
            'scroll_family':SCROLL.get(update,'unknown'),'palette_source':hex(palette),
            'static_palette_pointer':palette<=len(md)-128,
            'live_layer_count':'unverified for this level',
            'scroll_implementation':'MD uniform + bounded panorama' if level==0 else 'SNES background fallback pending complete MD layer adapter'}}
        rows.append(row)
        print(stem,name,'SNES',status,[(x['bg'],x['enabled_lines'],x['opaque_pixels_before_composition'],x['distinct_scroll_pairs']) for x in layers],
              'MD',row['md']['scroll_family'],flush=True)
    result={'schema':1,'rom_sha256':{'snes':hashlib.sha256(snes).hexdigest(),'md':hashlib.sha256(md).hexdigest()},
            'scope':'one initial native snapshot and mixed presentation per level; not complete temporal coverage',
            'levels':rows}
    (dest/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    table=['# Generated scene audit','','Per-scene sample frames and raw data: inventory.json.',
           '','BG occupancy is before priority, windows and colour math. An enabled plane is not a verified semantic layer.',
           '','| ID | Scene | Frame | SNES active BG / scroll pairs | MD update / family |', '|---|---|---|---|---|']
    for row in rows:
        bg=', '.join(f'BG{x["bg"]}: {x["distinct_scroll_pairs"]}' for x in row['snes']['layers'] if x['enabled_lines'])
        table.append(f'| {row["level"]} | {row["name"]} | {row["sample_frame"]} | {bg or row["snes"]["capture_status"]} | {row["md"]["update"]} / {row["md"]["scroll_family"]} |')
    (dest/'inventory.md').write_text('\n'.join(table)+'\n')

if __name__=='__main__': main()
