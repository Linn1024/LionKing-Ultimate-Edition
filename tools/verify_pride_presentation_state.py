"""Check the first displayed field after loading moving and paused mixed scenes."""
import json
import os
import argparse
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes, pixels


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group();group.add_argument('--paused-only',action='store_true');group.add_argument('--terrain-only',action='store_true')
    args=parser.parse_args()
    out=ROOT/('build/pride-terrain-presentation' if args.terrain_only else 'build/pride-presentation-state');out.mkdir(parents=True,exist_ok=True)
    native=out/'native.ini';native.write_text('schema = 1\ngame = snes\n')
    mixed=out/'mixed.ini'
    mixed.write_text('\n'.join(line for line in (ROOT/'profiles/pride-lands.ini').read_text().splitlines()
                              if not line.startswith(('audio.','gameplay.')))+'\n')
    if args.terrain_only:
        mixed.write_text(mixed.read_text()+'gameplay.levels.pride_lands.contacts = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
          '--no-pace','--no-audio','--no-record']
    def run(name,profile,frame,extra=(),capture=True,expect=0):
        log=out/(name+'.log');scene=out/(name+'.json');window=out/(name+'.png')
        cmd=base+['--resource-profile',str(profile),'--frames',str(frame),*map(str,extra)]
        if capture:cmd+=['--dump-window',str(window),'--dump-scene',str(scene)]
        env=os.environ.copy()
        env['TLK_WRAM_DUMP']=str(frame);env['TLK_WRAM_DIR']=str(out)
        with log.open('wb') as f:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
        assert result.returncode==expect,(name,result.returncode,log.read_text()[-1200:])
        return log,scene,window
    results=[]
    paused=out/'paused.polled.tape'
    for frame in ((3000,3100) if args.terrain_only else (1880,) if args.paused_only else (1700,1786,1848,3000,1880)):
        if frame==1880:
            env=os.environ.copy();env.update(TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(out))
            cmd=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(mixed),
                 '--frames',str(frame),'--input-polled',str(paused)]
            with (out/'pause-guest.log').open('wb') as f:subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
            ram=(out/f'hl_wram_{frame}.bin').read_bytes();assert struct.unpack_from('<H',ram,0xa89)[0],'fixture did not pause'
        active_tape=paused if frame==1880 else tape
        # Native-only saves must also retain history for a later media switch.
        reference=run(f'{frame}-continuous',mixed,frame+1,['--input-polled',active_tape])
        for source in ((mixed,) if args.terrain_only else (native,mixed)):
            name=f'{frame}-{source.stem}';state=out/(name+'.state')
            saved=run(name+'-save',source,frame,['--input-polled',active_tape,'--save-at',frame,state],False)
            used=int(re.search(r'tape_words_used=(\d+)',saved[0].read_text()).group(1))
            suffix=out/(name+'.polled.tape');suffix.write_bytes(active_tape.read_bytes()[used*2:])
            if frame==1848 and source==native:
                paused.write_bytes(tape.read_bytes()[:used*2]+struct.pack('<H',0x1000)+bytes(2000))
            resumed=run(name+'-loaded',mixed,frame+1,['--load',state,'--input-polled',suffix])
            assert hashes(reference[0])==hashes(resumed[0]),name+' guest state changed'
            assert json.loads(reference[1].read_text())==json.loads(resumed[1].read_text()),name+' scene history changed'
            assert pixels(reference[2])==pixels(resumed[2]),name+' first displayed field differs'
            results.append(name);print(name,'first loaded window identical PASS',flush=True)
    # Reject malformed presentation before it can be consumed by the renderer.
    raw=bytearray(state.read_bytes());at=36+struct.unpack_from('<Q',raw,24)[0]
    for name,offset,value in [('version',at+4+8,999),('pieces',at+4+12,513),('length',at,0xffffffff)]:
        broken=raw.copy();struct.pack_into('<I',broken,offset,value)
        path=out/('broken-'+name+'.state');path.write_bytes(broken)
        run('reject-'+name,mixed,frame+1,['--load',path],False,8)
    (out/'report.json').write_text(json.dumps({'result':'PASS','identical_first_fields':results,
        'malformed_history_rejected':3,'legacy_states_have_no_presentation_history':True},indent=2)+'\n')


if __name__=='__main__':main()
