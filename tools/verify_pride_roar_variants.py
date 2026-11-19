"""Compare held/repeated/attempted-air roars after ordinary idle clock alignment.

The MD reference idles 262 updates, versus 256 in the port. Those six additional
idle inputs align the pre-existing 32-update recharge phase. No guest edits or
runtime clock adjustments are used. Unaligned original captures remain available.
"""
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from pride_movement_audit import ROAR_VARIANTS
from verify_windows import hashes


def main():
    out = ROOT/'build/pride-roar-variants'
    out.mkdir(parents=True, exist_ok=True)
    capture = json.loads((ROOT/'build/pride-roar-original-aligned/md.json').read_text())
    assert capture['settle_frames'] == 262 and capture['tail_frames'] == 0
    catalog = json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    pairs = {int(row['snes'],16):{int(pose,16) for pose in row['md']}
             for group in ('exact_matches','pixel_art_variants') for row in catalog[group]}
    ready = ROOT/'build/pride-roar-behavior/snes-ready.state'
    profile = ROOT/'build/pride-roar-behavior/snes.ini'
    results = {}
    for name, protocol in ROAR_VARIANTS.items():
        original = capture['cases'][name]
        assert [row['pad'] for row in original] == protocol
        tape = out/(name+'.tape')
        tape.write_bytes(struct.pack('<'+str(2456+len(protocol))+'H', *([0]*2456+protocol)))
        runs = {}
        for mode in ('aot','lle'):
            folder = out/(name+'-'+mode)
            folder.mkdir(exist_ok=True)
            env = os.environ.copy()
            env.update(TLK_WRAM_DUMP=','.join(map(str,range(2457,2457+len(protocol)))), TLK_WRAM_DIR=str(folder))
            logpath = folder/'game.log'
            with logpath.open('wb') as log:
                subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'), '--rom',
                                str(ROOT/'Lion King, The (USA).sfc'), '--md-rom',
                                str(ROOT/'Lion King, The (World).md'), '--resource-profile', str(profile),
                                '--load', str(ready), '--frames', str(2456+len(protocol)), '--input', str(tape),
                                *(['--lle'] if mode=='lle' else [])], cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
            for index, expected in enumerate(original):
                ram = (folder/f'hl_wram_{2457+index}.bin').read_bytes()
                word = lambda address:struct.unpack_from('<H',ram,address)[0]
                draw = word(0xb21f)
                pose = int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff
                if index>=17:
                    assert expected['pose'] in pairs.get(pose,set()), (name,mode,index,'pose',hex(pose),hex(expected['pose']))
                md_roar = (expected['words'][24]<<16|expected['words'][25])==0x1966c6
                native_roar = word(0xb243)==0x589c and word(0xb245)==0xc3
                assert md_roar==native_roar, (name,mode,index,'action')
                if md_roar:
                    assert ram[0xb255] == expected['words'][33]>>8, (name,mode,index,'counter')
                assert word(0xa698)==expected['roar_active'], (name,mode,index,'active strength/window')
                assert word(0x2002)==expected['roar'], (name,mode,index,'recharge')
                assert word(0xb21d)==expected['y'] and word(0xb21b)+1==expected['x'], (name,mode,index,'position')
            runs[mode] = hashes(logpath)
        assert runs['aot']==runs['lle'], name+' execution modes differ'
        results[name] = {'fields':len(protocol), 'hashes':runs,
                         'original_pulse_strengths':[row['roar_active'] for row in original if row['roar_active']]}
        print(name,len(protocol),'original poses/action/strength/recharge/position fields PASS',flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,
        'reference_extra_idle_updates':6, 'runtime_clock_modified':False,
        'recharge_phase_aligned_by_inputs':True,'cases':results},indent=2)+'\n')


if __name__ == '__main__':
    main()
