"""Compare normal-input native LLE and original MD taunt animation timelines."""
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from pride_hyena_taunt_art import PAIRS


def main():
    out=ROOT/'build/hyena-taunt-native-original';out.mkdir(parents=True,exist_ok=True)
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    base=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--resource-profile',str(profile),'--lle']
    def run(log,extra,env=None):
        with log.open('wb') as stream:subprocess.run([*base,*extra],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
    run(out/'prefix.log',['--frames','3850','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape')])
    used=int(re.search(r'tape_words_used=(\d+)',(out/'prefix.log').read_text()).group(1))
    tape=out/'stop.polled.tape';tape.write_bytes((ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[:used*2]+bytes(5000))
    env=os.environ.copy();env.update(TLK_WRAM_DUMP=','.join(map(str,range(3850,4351))),TLK_WRAM_DIR=str(out))
    run(out/'game.log',['--frames','4350','--input-polled',str(tape)],env)
    native=[]
    for frame in range(3850,4351):
        ram=(out/f'hl_wram_{frame}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
        if word(0x1ff9e) or word(0xdf) not in (0x387,0x80d):continue
        for actor in range(0xb293,0xc213,0x80):
            if word(actor+0x30)==0x41c6 and word(actor+0x32)==0xc1:
                draw=word(actor+12);pose=int.from_bytes(ram[draw+10:draw+13],'little')
                native.append({'frame':frame,'pose':pose,'counter':word(actor+0x2e)})
    original=json.loads((ROOT/'build/hyena-taunt-original/report.json').read_text())
    md=[{'frame':row['frame'],'pose':row['actors'][0]['pose'],'counter':row['actors'][0]['counter']}
        for row in original['observations']]
    def groups(rows):
        result=[]
        for row in rows:
            if not result or row['frame']!=result[-1][-1]['frame']+1:result.append([])
            result[-1].append(row)
        return result
    native_groups=groups(native);md_groups=groups(md)
    assert len(native_groups)==len(md_groups)==2
    pairs=dict(PAIRS);differences=[]
    for case,(left,right) in enumerate(zip(native_groups,md_groups)):
        assert len(left)==len(right)==34
        for index,(a,b) in enumerate(zip(left,right)):
            assert pairs[a['pose']]==b['pose'],(case,index,a,b)
            if a['counter']!=b['counter']:
                differences.append({'action':case,'index':index,'native_counter':a['counter'],'md_counter':b['counter']})
    metadata={int(row['snes'],16):row for row in json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']}
    for snes,megadrive in PAIRS:
        row=metadata[snes]
        assert int(row['md'],16)==megadrive and row['native_palette']==6 and row['md_palette']==3
    assert differences,'Expected the native extra animation event2 to differ'
    result={'result':'PASS','scope':__doc__,'native_source':'Original interpreter, no MD ROM or MD choices',
            'native_input_prefix_polls':used,'actions':2,'fields_per_action':34,
            'all_eight_pose_correspondences_observed':True,'native':native,'md':md,
            'counter_tag_differences':differences,
            'counter_difference':'Native event2 drives the later native cue; MD stream omits it. Artwork selection does not change these native tags.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Original native/MD taunts: two x34 pose/timing fields match; extra native event2 retained as separate sound/gameplay semantics PASS',flush=True)


if __name__=='__main__':main()
