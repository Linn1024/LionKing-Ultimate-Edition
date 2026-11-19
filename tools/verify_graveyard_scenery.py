"""Verify Elephant Graveyard media, moving save fields and normal completion.

Uses the existing credited All Bugs controller tape. Presentation never edits
positions, actors, collision or other guest gameplay state.
"""
import json,os,re,struct,subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    out=ROOT/'build/graveyard-verification';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    choices={'snes':'','native320':'display.viewport = md\n',
             'background':'display.viewport = md\ngraphics.scenery.background = md\n',
             'scenery':'display.viewport = md\ngraphics.scenery = md\n'}
    profiles={}
    for name,extra in choices.items():
        p=out/(name+'.ini');p.write_text('schema = 1\ngame = snes\n'+extra);profiles[name]=p
    tape=ROOT/'engine/tapes/allbugsF.read.tape';head=ROOT/'engine/build-win/tlk_headless.exe';sdl=ROOT/'dist/LionKing.exe'
    common=['--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md')]
    def run(name,host,profile,end,extra=(),capture=False,dump=False):
        log=out/(name+'.log');cmd=[str(host),*common,'--resource-profile',str(profiles[profile]),'--frames',str(end),*map(str,extra)]
        env=os.environ.copy()
        if host==sdl:cmd+=['--config',str(config),'--no-pace','--no-audio','--no-record']
        if capture:cmd+=['--dump-window',str(out/(name+'.png')),'--dump-scene',str(out/(name+'.json'))]
        if dump:env.update(TLK_WRAM_DUMP=str(end),TLK_WRAM_DIR=str(out))
        with log.open('wb') as f:subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
        return hashes(log),int(re.search(r'tape_words_used=(\d+)',log.read_text()).group(1)) if '--input-polled' in cmd else 0
    state=out/'moving.state'
    _,used=run('prepare',head,'snes',13500,['--input-polled',tape,'--save-at',13500,state],dump=True)
    ram=(out/'hl_wram_13500.bin').read_bytes();assert struct.unpack_from('<H',ram,0x1ff9e)[0]==2 and struct.unpack_from('<H',ram,0xdf)[0]==0x3eb,'Wrong scene fixture'
    suffix=out/'after13500.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:]);pictures={}
    for profile in ('native320','background','scenery'):
        value,_=run('window-'+profile,sdl,profile,14300,['--load',state,'--input-polled',suffix],True)
        scene=json.loads((out/('window-'+profile+'.json')).read_text());assert scene['level']==2 and scene['stage_detected']
        pictures[profile]=value
    assert len(pictures['native320'])==2 and len({tuple(v.items()) for v in pictures.values()})==1,'Scenery changed guest state'
    a=pixels(out/'window-native320.png');b=pixels(out/'window-background.png');c=pixels(out/'window-scenery.png')
    assert a[:2]==b[:2]==c[:2]==(640,448) and a!=b and b!=c,'Scenery choices were not independent/visible'
    # Save during movement; compare the very first field after loading.
    reference,_=run('continuous',sdl,'background',13601,['--load',state,'--input-polled',suffix],True)
    saved=[]
    for profile in ('snes','background'):
        save=out/(profile+'-13600.state');_,used=run('save-'+profile,sdl,profile,13600,['--load',state,'--input-polled',suffix,'--save-at',13600,save])
        after=out/(profile+'-13600.polled.tape');after.write_bytes(suffix.read_bytes()[used*2:])
        actual,_=run('loaded-'+profile,sdl,'background',13601,['--load',save,'--input-polled',after],True)
        assert actual==reference and pixels(out/('loaded-'+profile+'.png'))==pixels(out/'continuous.png'),profile+' first loaded field differs'
        assert json.loads((out/('loaded-'+profile+'.json')).read_text())==json.loads((out/'continuous.json').read_text())
        saved.append(profile);print(profile,'moving loaded first field identical PASS',flush=True)
    results={}
    for mode,profile,flags in [('native','snes',[]),('md-aot','background',[]),('md-lle','background',['--lle'])]:
        value,_=run('complete-'+mode,head,profile,19400,['--load',state,'--input-polled',suffix,'--ram-log',out/(mode+'.ram'),*flags])
        results[mode]=value
        rows=[r.split() for r in (out/(mode+'.ram')).read_text().splitlines()]
        assert any(int(r[6],16)==3 for r in rows),'Did not reach Stampede after Elephant Graveyard'
        print(mode,'ordinary input completion PASS',flush=True)
    assert results['native']==results['md-aot']==results['md-lle'],'Complete route guest hashes differ'
    assert (out/'native.ram').read_bytes()==(out/'md-aot.ram').read_bytes()==(out/'md-lle.ram').read_bytes(),'Tracked route differs'
    report={'result':'PASS','scope':__doc__,'independent_windows_guest_hashes':pictures,'moving_first_field_profiles':saved,'completion_hashes':results}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Elephant Graveyard background, independent scenery, saves and completion PASS',flush=True)


if __name__=='__main__':main()
