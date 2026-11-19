"""Retain original health-death lifecycle differences separately from audio choice.

Different ordinary controller approaches reach the same checkpoint/health-death
kind. Compare observable ordering relative to health zero, not absolute route
coordinates, RNG or cross-console frame synchronization.
"""
import hashlib
import json
import argparse
import re
import subprocess
from audit_scenes import ROOT, read_rom


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def counter_contract():
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert snes[0x1cb:0x1cf]==bytes.fromhex('afaaff7f')
    assert snes[0x1e0:0x1e3]==bytes.fromhex('8d0a20')
    assert md[0x8fa3c:0x8fa42]==bytes.fromhex('3039ffffccee')
    assert md[0x8fa5e:0x8fa60]==bytes.fromhex('5340')
    starts={}
    for name,sp,mp in [('easy',0x3c162,0x1d6b26),('normal',0x3c176,0x1d6b14),('hard',0x3c18b,0x1d6b30)]:
        assert snes[sp]==0xa9 and snes[sp+3:sp+7]==bytes.fromhex('8faaff7f')
        assert md[mp:mp+2]==bytes.fromhex('33fc') and md[mp+4:mp+8]==bytes.fromhex('ffffccee')
        native=int.from_bytes(snes[sp+1:sp+3],'little');other=int.from_bytes(md[mp+2:mp+4],'big')
        assert native+1==other
        starts[name]={'native_spares':native,'md_total':other,'normalized_starting_total':other}
    assert snes[0x8af3:0x8af9]==bytes.fromhex('afaaff7ff029')
    assert md[0x1d6cb2:0x1d6cba]==bytes.fromhex('4a79ffffccee6700')
    assert 0x1d6cba+int.from_bytes(md[0x1d6cba:0x1d6cbc],'big',signed=True)==0x1d6874
    contracts={}
    for name,rom,start,end in [('native_hud',snes,0x1cb,0x1e3),('md_hud',md,0x8fa3c,0x8fa6a),
                               ('native_initial',snes,0x3c162,0x3c196),('md_initial',md,0x1d6b14,0x1d6b38),
                               ('native_final_life',snes,0x8af3,0x8afe),('md_final_life',md,0x1d6cb2,0x1d6ce0)]:
        contracts[name]={'rom_offset_range':[start,end],'sha256':hashlib.sha256(rom[start:end]).hexdigest()}
    return {'native_counter':'spare lives, excluding current life','md_counter':'total lives, including current life',
            'native_hud':'uses native spare count directly','md_hud':'subtracts1 at08FA5E before glyph indexing',
            'initial_difficulty_counts':starts,'raw_write_timing_alone_justifies_life_counter_patch':False,
            'final_life':'native spare0 corresponds to MD total1 before decrement; MD post-decrement0 skips430',
            'original_contracts':contracts}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-native',action='store_true',help='Reproduce original native LLE power-on prefix and neutral health death')
    args=parser.parse_args()
    folder=ROOT/'build/pride-health-death-native';folder.mkdir(exist_ok=True)
    source=folder/'game.ram'
    if args.capture_native:
        profile=folder/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
        original_tape=ROOT/'engine/tapes/allbugsF.read.tape'
        base=[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc',
              '--resource-profile',profile,'--lle']
        with (folder/'prefix.log').open('wb') as f:
            subprocess.run(list(map(str,base+['--frames','3740','--input-polled',original_tape])),
                           cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        used=int(re.search(r'tape_words_used=(\d+)',(folder/'prefix.log').read_text()).group(1))
        tape=folder/'neutral-tail.polled.tape';tape.write_bytes(original_tape.read_bytes()[:used*2]+bytes(5000))
        with (folder/'game.log').open('wb') as f:
            subprocess.run(list(map(str,base+['--frames','5400','--input-polled',tape,'--ram-log',source])),
                           cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        (folder/'provenance.json').write_text(json.dumps({'source':'Existing credited SNES All Bugs tape; ordinary power-on and neutral tail',
            'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),'tracked_ram_sha256':digest(source),
            'original_tape_sha256':hashlib.sha256(original_tape.read_bytes()).hexdigest(),'retained_polls':used,
            'neutral_tail_polls':2500,'tape_sha256':hashlib.sha256(tape.read_bytes()).hexdigest(),
            'original_native_lle':True,'loaded_states':False,'md_rom_or_choices':False},indent=2)+'\n')
    original=ROOT/'build/pride-health-death-original/life-report.json'
    provenance=json.loads((folder/'provenance.json').read_text())
    assert provenance['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe'),'Recapture native lifecycle for this binary'
    assert provenance['tracked_ram_sha256']==digest(source),'Native lifecycle capture changed'
    conventions=counter_contract()
    md=json.loads(original.read_text());assert md['result']=='PASS' and md['one_life_lost']
    rows=[r.split() for r in source.read_text().splitlines()]
    def value(row,i):return int(row[i],16)
    death=next(int(r[0]) for r in rows if int(r[0])>4000 and value(r,6)==0 and value(r,3)==0)
    loss=next(int(b[0]) for a,b in zip(rows,rows[1:]) if int(b[0])>=death and value(b,7)<value(a,7))
    restored=next(int(r[0]) for r in rows if int(r[0])>=loss and value(r,3)>0)
    native={'health_zero':death,'life_loss':loss,'health_restored':restored,
            'health_zero_to_life_loss_fields':loss-death,'health_zero_to_restored_fields':restored-death}
    other={'health_zero':md['death_frame'],'life_loss':md['life_loss_frame'],
           'health_restored':md['health_restored_frame'],
           'health_zero_to_life_loss_fields':md['life_loss_frame']-md['death_frame'],
           'health_zero_to_restored_fields':md['health_restored_frame']-md['death_frame']}
    assert native['health_zero_to_life_loss_fields']>300
    assert other['health_zero_to_life_loss_fields']<native['health_zero_to_life_loss_fields']
    phases=[]
    native_rows=[next(r for r in rows if int(r[0])==f) for f in (death-1,death,restored)]
    for label,native_row,md_row in zip(('alive_before_death','health_zero','restored'),native_rows,md['milestones']):
        spares=value(native_row,7);health=value(native_row,3)
        # At health zero the current native life has already been spent; the
        # spare count is the future playable lives. Once revived, add current.
        available=spares+int(health>0)
        assert available==md_row['lives'],(label,available,md_row)
        phases.append({'phase':label,'native_frame':int(native_row[0]),'native_spares':spares,
                       'native_current_life_available':health>0,'normalized_available_lives':available,
                       'md_frame':md_row['frame'],'md_stored_total':md_row['lives']})
    out=ROOT/'build/pride-death-lifecycle';out.mkdir(exist_ok=True)
    report={'result':'COUNTER_CONVENTIONS_VERIFIED_DEATH_TIMING_OPEN','scope':__doc__,'native':native,'md':other,
            'counter_conventions':conventions,
            'normalized_life_count_milestones':phases,
            'same_absolute_trajectory_or_rng_asserted':False,'independent_death_gameplay_source_available':False,
            'new_death_music_adapter_does_not_replace_guest_lifecycle':True,
            'source_sha256':{'native_tracked_ram':hashlib.sha256(source.read_bytes()).hexdigest(),
                             'native_headless':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest(),
                             'native_provenance':hashlib.sha256((folder/'provenance.json').read_bytes()).hexdigest(),
                             'md_life_report':hashlib.sha256(original.read_bytes()).hexdigest()},
            'remaining':['Original death timer/animation/fade and normalized life-count lifecycle contract',
                         'Independent MD gameplay source with original checkpoint/game-over and save/yield behavior']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Counter conventions verified; raw write delays',loss-death,'vs',other['health_zero_to_life_loss_fields'],
          'fields do not alone justify a counter patch; death presentation/timing remains open',flush=True)


if __name__=='__main__':main()
