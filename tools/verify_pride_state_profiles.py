"""Check saved gameplay sources, compatible continuation and mismatch rejection."""
import hashlib
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes

def main():
    dest=ROOT/'build/pride-state-profiles';dest.mkdir(parents=True,exist_ok=True)
    (dest/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    choices={
        'snes':'',
        'camera256':'gameplay.camera = md\n',
        'camera320':'gameplay.camera = md\ndisplay.viewport = md\n',
        'pickups':'gameplay.levels.pride_lands.pickups = md\ndisplay.viewport = md\n',
        'both':'gameplay.camera = md\ngameplay.levels.pride_lands.pickups = md\ndisplay.viewport = md\n',
        'leaves':'gameplay.levels.pride_lands.leaves = md\ndisplay.viewport = md\n',
        'contacts':'gameplay.levels.pride_lands.contacts = md\ndisplay.viewport = md\n',
        'roar':'gameplay.simba.roar = md\n',
        'start':'gameplay.levels.pride_lands.start = md\n',
        'activation':'gameplay.levels.pride_lands.activation = md\n',
        'reactivation':'gameplay.levels.pride_lands.lizard_reactivation = md\n',
        'body-simba':'gameplay.hitboxes.simba = md\n',
        'body-enemies':'gameplay.hitboxes.enemies = md\n',
        'body-both':'gameplay.hitboxes = md\n',
        'ceiling':'gameplay.levels.pride_lands.ceiling_rows = md\n',
        'ceiling-clearance':'gameplay.levels.pride_lands.ceiling_clearance = md\n',
        'streaming-top':'gameplay.levels.pride_lands.streaming_top = md\n',
        'ceiling-both':'gameplay.levels.pride_lands.ceiling = md\n',
        'all-gameplay':'gameplay.camera = md\ngameplay.levels.pride_lands.pickups = md\ngameplay.levels.pride_lands.leaves = md\ngameplay.levels.pride_lands.contacts = md\ngameplay.simba.roar = md\ndisplay.viewport = md\n',
        'media':'graphics.scenery = md\ndisplay.viewport = md\n',
    }
    profiles={}
    choices['all-gameplay']+='gameplay.levels.pride_lands.start = md\n'
    choices['all-gameplay']+='gameplay.levels.pride_lands.activation = md\ngameplay.levels.pride_lands.lizard_reactivation = md\n'
    choices['all-gameplay']+='gameplay.hitboxes = md\n'
    choices['all-gameplay']+='gameplay.levels.pride_lands.ceiling_rows = md\n'
    choices['all-gameplay']+='gameplay.levels.pride_lands.ceiling_clearance = md\n'
    choices['all-gameplay']+='gameplay.levels.pride_lands.streaming_top = md\n'
    for name,extra in choices.items():
        path=dest/(name+'.ini');path.write_text('schema = 1\ngame = snes\n'+extra);profiles[name]=path
    def run(name,source,extra=(),expect=0,message=''):
        command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profiles[source]),
                 '--frames','2400','--input',str(ROOT/'engine/build/playtapes/l00_right.tape'),*map(str,extra)]
        folder=dest/name;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env['TLK_WRAM_DUMP']='1800';env['TLK_WRAM_DIR']=str(folder)
        log=dest/(name+'.log')
        with log.open('wb') as output:
            result=subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=120)
        text=log.read_text(errors='replace')
        assert result.returncode==expect,(name,result.returncode,text[-1500:])
        if message:assert message in text,(name,text[-1500:])
        return hashes(log)
    results={};states={}
    for name in ('snes','camera256','camera320','pickups','both','leaves','contacts','roar','start','activation','reactivation','body-simba','body-enemies','body-both','ceiling','ceiling-clearance','ceiling-both','streaming-top','all-gameplay'):
        state=dest/(name+'.state');states[name]=state
        baseline=run(name+'-continuous',name,['--save-at','1800',state])
        ram=(dest/(name+'-continuous')/'hl_wram_1800.bin').read_bytes()
        assert struct.unpack_from('<H',ram,0xdf)[0] in (0x387,0x80d),'fixture saved outside actual Pride Lands'
        resumed=run(name+'-resumed',name,['--load',state])
        assert len(baseline)==2 and baseline==resumed,name+' matching-source state did not resume exactly'
        assert struct.unpack_from('<I',state.read_bytes(),8)[0]==4,'state source metadata was not versioned'
        if name.startswith('body-'):
            mask={'body-simba':0x01000000,'body-enemies':0x02000000,'body-both':0x03000000}[name]
            assert struct.unpack_from('<I',state.read_bytes(),32)[0]&0x03000000==mask
        if name.startswith('ceiling'):
            mask={'ceiling':0x04000000,'ceiling-clearance':0x08000000,'ceiling-both':0x0c000000}[name]
            assert struct.unpack_from('<I',state.read_bytes(),32)[0]&0x0f0000ff==mask
        if name=='streaming-top':assert struct.unpack_from('<I',state.read_bytes(),32)[0]&0x1f0000ff==0x10000000
        results[name]=baseline;print(name,'matching-source continuation PASS',flush=True)
    # The pickup index is built during loading; also resume before it exists.
    early=dest/'pickup-loading.state'
    baseline=run('pickup-loading-continuous','pickups',['--save-at','600',early])
    assert baseline==run('pickup-loading-resumed','pickups',['--load',early]),'pickup loader resume differs'
    assert run('neutral-scene-new-source','snes',['--load',early])==results['snes'],'neutral transition incorrectly kept MD layout rules'
    assert run('native-state-other-media','media',['--load',states['snes']])==results['snes'],'media choices blocked or changed guest state'
    mismatches=[('snes','camera256','camera source'),('camera256','snes','camera source'),
                ('snes','pickups','pickup source'),('pickups','snes','pickup source'),
                ('snes','leaves','leaf behavior'),('leaves','snes','leaf behavior'),
                ('snes','contacts','terrain contact source'),('contacts','snes','terrain contact source'),
                ('snes','roar','roar behavior'),('roar','snes','roar behavior'),
                ('snes','start','initial position source'),('start','snes','initial position source'),
                ('snes','activation','initial enemy activation'),('activation','snes','initial enemy activation'),
                ('snes','reactivation','lizard reactivation'),('reactivation','snes','lizard reactivation'),
                ('snes','body-simba','Simba body bounds'),('body-simba','snes','Simba body bounds'),
                ('snes','body-enemies','enemy body bounds'),('body-enemies','snes','enemy body bounds'),
                ('body-simba','body-enemies','Simba body bounds'),('body-enemies','body-simba','Simba body bounds'),
                ('snes','ceiling','ceiling row'),('ceiling','snes','ceiling row'),
                ('snes','ceiling-clearance','ceiling clearance'),('ceiling-clearance','snes','ceiling clearance'),
                ('ceiling','ceiling-clearance','ceiling row'),('ceiling-clearance','ceiling','ceiling row'),
                ('snes','streaming-top','streaming top margin'),('streaming-top','snes','streaming top margin'),
                ('camera256','camera320','320-pixel'),('camera320','camera256','256-pixel')]
    # Tuples are active profile, saved-state profile, expected reason.
    for active,saved,message in mismatches:
        before=hashlib.sha256(states[saved].read_bytes()).hexdigest()
        run('reject-'+saved+'-as-'+active,active,['--load',states[saved]],8,message)
        assert hashlib.sha256(states[saved].read_bytes()).hexdigest()==before,'rejected state file changed'
    raw=states['snes'].read_bytes();legacy=bytearray(raw[:32]);struct.pack_into('<I',legacy,8,1)
    legacy.extend(raw[36:36+struct.unpack_from("<Q",raw,24)[0]]);old=dest/'legacy-native.state';old.write_bytes(legacy)
    assert run('legacy-native','snes',['--load',old])==results['snes'],'legacy native state regressed'
    run('legacy-with-md-rules','pickups',['--load',old],8,'Older state')
    run('legacy-with-md-contacts','contacts',['--load',old],8,'Older state')
    run('legacy-with-md-roar','roar',['--load',old],8,'Older state')
    run('legacy-with-md-start','start',['--load',old],8,'Older state')
    run('legacy-with-md-activation','activation',['--load',old],8,'Older state')
    run('legacy-with-md-reactivation','reactivation',['--load',old],8,'Older state')
    run('legacy-with-md-body-simba','body-simba',['--load',old],8,'Older state')
    run('legacy-with-md-body-enemies','body-enemies',['--load',old],8,'Older state')
    run('legacy-with-md-ceiling','ceiling',['--load',old],8,'Older state')
    run('legacy-with-md-ceiling-clearance','ceiling-clearance',['--load',old],8,'Older state')
    run('legacy-with-md-streaming-top','streaming-top',['--load',old],8,'Older state')
    for name in ('snes','all-gameplay'):
        raw=bytearray(states[name].read_bytes());struct.pack_into('<I',raw,8,2)
        old=dest/('legacy-v2-'+name+'.state')
        old.write_bytes(raw[:36+struct.unpack_from('<Q',raw,24)[0]])
        assert run('legacy-v2-'+name,name,['--load',old])==results[name],name+' v2 state regressed'
    raw=bytearray(states['snes'].read_bytes());struct.pack_into('<I',raw,8,3)
    at=36+struct.unpack_from('<Q',raw,24)[0];end=at+4+struct.unpack_from('<I',raw,at)[0]
    old=dest/'legacy-v3.state';old.write_bytes(raw[:end])
    assert run('legacy-v3','snes',['--load',old])==results['snes'],'v3 state regressed'
    report={'result':'PASS','matching_source_hashes':results,'pickup_loading_resume':True,'legacy_v3_native_load':True,
            'graphics_profile_compatible':True,'neutral_transition_source_change':True,'mismatches_rejected_before_load':len(mismatches),
            'legacy_native_state_loads':True,'legacy_v2_native_and_md_gameplay_load':True,'legacy_unknown_md_rules_rejected':True}
    (dest/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Gameplay-source save compatibility PASS',flush=True)

if __name__=='__main__':main()
