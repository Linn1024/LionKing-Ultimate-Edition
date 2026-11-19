"""Check shared leaf artwork, independent MD colours and complete route coverage."""
import json
import os
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    out=ROOT/'build/pride-leaf-verification';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    choices={'native':'','frames':'graphics.sprites.leaves.frames = md\n',
             'palette':'graphics.sprites.leaves.palette = md\n','both':'graphics.sprites.leaves = md\n'}
    results={};pictures={}
    def run(name,extra,frames=1786,mode='aot'):
        profile=out/(name+'.ini');profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+extra)
        env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(out/(name+'-coverage.json'))
        command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
                 '--resource-profile',str(profile),'--frames',str(frames),
                 '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
                 '--no-pace','--no-audio','--no-record','--dump-window',str(out/(name+'.png'))]
        if mode=='lle':command.append('--lle')
        log=out/(name+'.log')
        with log.open('wb') as stream:
            subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        value=hashes(log);assert len(value)==2
        return value,json.loads((out/(name+'-coverage.json')).read_text())
    for name,extra in choices.items():
        value,coverage=run(name,extra);results[name]={'hashes':value,'coverage':coverage}
        width,height,image=pixels(out/(name+'.png'));assert (width,height)==(960,672)
        pictures[name]=image
    assert all(r['hashes']==results['native']['hashes'] for r in results.values()),'Leaf presentation changed guest state'
    assert pictures['frames']==pictures['native'],'Shared anchored leaf artwork changed pixels'
    assert pictures['both']==pictures['palette'],'Shared MD leaf frames changed independently selected colours'
    changed=[i for i,(a,b) in enumerate(zip(pictures['native'],pictures['palette'])) if a!=b]
    assert changed and len(changed)<1500,'Leaf palette is invisible or changed unrelated large artwork'
    complete={}
    for mode in ('aot','lle'):
        value,coverage=run('complete-'+mode,choices['both'],5000,mode)
        assert coverage['seen_by_role']['leaves']==17,'Leaf animation coverage incomplete'
        assert not coverage['missing_poses'] and not coverage['missing_npc_poses'],'Missing observed first-level art'
        complete[mode]={'hashes':value,'coverage':coverage}
    assert complete['aot']==complete['lle'],'Leaf full route differs between execution modes'
    baseline=json.loads((ROOT/'build/pride-baseline/report.json').read_text())['hashes']
    assert complete['aot']['hashes']==baseline,'Leaf graphics changed the native completed route'
    report={'result':'PASS','shared_anchored_art_identical':True,'independent_palette_changed_pixels':len(changed),
            'guest_hashes_unchanged':True,'complete_route':complete,'captures':results}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Pride leaves: shared artwork, independent palette, 17 poses and full AOT/LLE route PASS',flush=True)


if __name__=='__main__':main()
