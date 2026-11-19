"""Derive a local controller-only route and compare its first movement fields.

Use the existing SNES ordinary boot prefix, followed by mapped inputs from the
unforced original MD movie's first rightward input. Recordings remain ignored.
This diagnoses remaining behavior differences, not completed level fidelity.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit',action='store_true')
    parser.add_argument('--ceiling-rows',choices=('snes','md'),default='snes')
    parser.add_argument('--ceiling-clearance',choices=('snes','md'),default='snes')
    parser.add_argument('--streaming-top',choices=('snes','md'),default='snes')
    parser.add_argument('--out',type=Path,default=ROOT/'build/pride-md-controller-route')
    parser.add_argument('--frames',type=int,default=1100);parser.add_argument('--lle',action='store_true')
    parser.add_argument('--dump-fields',default=','.join(map(str,range(1030,1039))))
    args=parser.parse_args()
    source=ROOT/'build/md-next-levels-replay/frames.json';rows=json.loads(source.read_text())
    events=[];previous=0
    for row in rows:
        if row['poll']>previous:
            assert row['poll']==previous+1
            events.append(row['pad'])
        previous=row['poll']
    start=next(i for i,pad in enumerate(events) if pad&128)
    raw=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes();words=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
    prefix=words[:words.index(0x100)]
    bits=[(7,0x100),(6,0x200),(5,0x400),(4,0x800),(8,0x8000),(1,0x80),(0,0x4000),(3,0x1000)]
    converted=[sum(value for bit,value in bits if pad&(1<<bit)) for pad in events[start:]]
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    tape=out/'derived.polled.tape';tape.write_bytes(struct.pack('<'+'H'*(len(prefix)+len(converted)),*(prefix+converted)))
    provenance={'scope':__doc__,'original_source':'https://tasvideos.org/10612S','author':'ShgofcTAS',
        'original_frames_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'snes_prefix_polls':len(prefix),'md_source_cut':start,'mapped_polls':len(converted),
        'tape_sha256':hashlib.sha256(tape.read_bytes()).hexdigest(),'actor_or_world_edits':False}
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    if not args.audit:return
    profile=out/'resources.ini'
    base=[line for line in (ROOT/'build/pride-state-profiles/all-gameplay.ini').read_text().splitlines()
          if not line.strip().startswith(('gameplay.levels.pride_lands.ceiling_rows','gameplay.levels.pride_lands.ceiling_clearance','gameplay.levels.pride_lands.streaming_top'))]
    profile.write_text('\n'.join(base)+'\ngameplay.levels.pride_lands.ceiling_rows = '+args.ceiling_rows+
        '\ngameplay.levels.pride_lands.ceiling_clearance = '+args.ceiling_clearance+'\ngameplay.levels.pride_lands.streaming_top = '+args.streaming_top+'\n')
    host=ROOT/'engine/build-win/tlk_headless.exe';ram=out/'native-probe.ram'
    env=os.environ.copy();env.update(TLK_WRAM_DUMP=args.dump_fields,TLK_WRAM_DIR=str(out),
        TLK_FRAME_LOG=str(out/'frame-fnv.log'),TLK_CEILING_TRACE=str(out/'ceiling.csv'),
        TLK_STREAMING_TOP_TRACE=str(out/'streaming-top.csv'))
    cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--frames',args.frames,'--input-polled',tape,'--ram-log',ram]
    if args.lle:cmd+=['--lle']
    with (out/'native-probe.log').open('wb') as f:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
    tracked=[r.split() for r in ram.read_text().splitlines()]
    native=[{'frame':int(r[0]),'xy':[int(r[4],16),int(r[5],16)]} for r in tracked if int(r[0])>930]
    original=[r for r in rows if r['level']==0 and r['player'] is not None and r['frame']<4360]
    ni=next(i for i,r in enumerate(native) if r['xy'][0]>65)
    mi=next(i for i,r in enumerate(original) if r['player'][0]>65)
    checked=0;gap=None
    for a,b in zip(native[ni:],original[mi:]):
        if a['xy']!=b['player']:
            gap={'native_frame':a['frame'],'md_frame':b['frame'],'native_xy':a['xy'],'md_xy':b['player']};break
        checked+=1
    # Display fields cease to align when one original needs extra lag fields.
    # Retain the literal field comparison above, but diagnose gameplay using
    # controller-read updates. No actor/world data is edited or normalized.
    updates=[{'frame':int(r[0]),'xy':[int(r[4],16),int(r[5],16)]}
             for r in tracked if int(r[0])>930 and r[1]=='0']
    md_updates=[];previous=0
    for row in rows:
        if row['poll']>previous and row['level']==0 and row['player'] is not None and row['frame']<4360:
            md_updates.append(row)
        previous=row['poll']
    ui=next(i for i,r in enumerate(updates) if r['xy'][0]>65)
    oi=next(i for i,r in enumerate(md_updates) if r['player'][0]>65)
    matched_updates=0;update_gap=None
    for a,b in zip(updates[ui:],md_updates[oi:]):
        if a['xy']!=b['player']:
            update_gap={'native_frame':a['frame'],'md_frame':b['frame'],'native_xy':a['xy'],'md_xy':b['player']};break
        matched_updates+=1
    report={'result':'PARTIAL' if gap else 'PASS','scope':__doc__,'matched_initial_integer_position_fields':checked,
        'first_gap':gap,'headless_sha256':hashlib.sha256(host.read_bytes()).hexdigest(),
        'matched_initial_nonlag_integer_position_updates':matched_updates,'first_nonlag_gap':update_gap,
        'profile_sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'tape_sha256':provenance['tape_sha256'],
        'ceiling_row_source':args.ceiling_rows,'execution_mode':'lle' if args.lle else 'aot',
        'ceiling_clearance_source':args.ceiling_clearance,'streaming_top_source':args.streaming_top,
        'frames':args.frames,'final_level':int(tracked[-1][6],16),
        'first_level_completed':any(int(r[0])>1000 and int(r[6],16)==1 for r in tracked),
        'full_level_fidelity_complete':False}
    (out/'early-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MD controller-route early positions:',checked,'matching fields; first gap',gap,flush=True)


if __name__=='__main__':main()
