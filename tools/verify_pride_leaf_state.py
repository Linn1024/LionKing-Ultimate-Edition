"""Resume normal input immediately around original Pride leaf emission."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-leaf-state';out.mkdir(parents=True,exist_ok=True)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.leaves = md\naudio.effects.world.leaves = md\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    base=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile)]
    def run(name,extra,env=None):
        log=out/(name+'.log')
        with log.open('wb') as stream:subprocess.run(base+list(map(str,extra)),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        return hashes(log),log.read_text()
    expected,_=run('continuous',['--frames','2000','--input-polled',tape])
    results=[]
    for frame in range(1698,1706):
        state=out/f'{frame}.state'
        _,text=run(f'prepare-{frame}',['--frames',frame,'--input-polled',tape,'--save-at',frame,state])
        used=int(re.search(r'tape_words_used=(\d+)',text).group(1))
        suffix=out/f'{frame}.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
        modes={}
        for mode in ('aot','lle'):
            actual,_=run(f'resume-{frame}-{mode}',['--load',state,'--frames','2000','--input-polled',suffix]+(['--lle'] if mode=='lle' else []))
            assert actual==expected,(frame,mode,actual,expected)
            modes[mode]=actual
        results.append({'saved_frame':frame,'hashes':modes})
        print('Leaf emitter save',frame,'normal input AOT/LLE continuation PASS',flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','hashes':expected,'cases':results},indent=2)+'\n')


if __name__=='__main__':main()
