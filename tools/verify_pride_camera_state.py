"""Exercise camera save/load in new processes and capture both actual windows."""
import json
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes

def main():
    dest=ROOT/'build/pride-camera-verification';dest.mkdir(parents=True,exist_ok=True)
    base=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--frames','2400',
          '--input',str(ROOT/'engine/build/playtapes/l00_right.tape')]
    result={}
    for width in (256,320):
        profile=dest/f'{width}.ini';state=dest/f'{width}.state'
        common=base+['--resource-profile',str(profile),'--wide',str(width)]
        for name,extra in [('continuous',['--save-at','1800',str(state)]),('resumed',['--load',str(state)])]:
            log=dest/f'state-{width}-{name}.log'
            with log.open('wb') as output:
                subprocess.run(common+extra,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=120)
        a=hashes(dest/f'state-{width}-continuous.log');b=hashes(dest/f'state-{width}-resumed.log')
        assert len(a)==2 and a==b,f'{width} camera state did not resume exactly'
        window_profile=dest/f'window-{width}.ini'
        window_profile.write_text(profile.read_text()+'graphics.scenery = md\n')
        cmd=[str(ROOT/'engine/build-win/tlk_sdl.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(window_profile),
             '--config',str(ROOT/'build/pride-mix-verification/host.ini'),'--frames','1400',
             '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--no-pace','--no-audio','--no-record',
             '--dump-window',str(dest/f'md-scenery-{width}.png'),'--dump-scene',str(dest/f'md-scenery-{width}.json')]
        with (dest/f'window-{width}.log').open('wb') as output:
            subprocess.run(cmd,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=120)
        scene=json.loads((dest/f'md-scenery-{width}.json').read_text())
        assert scene['level']==0 and scene['stage_detected'],'window was not Pride Lands'
        result[str(width)]={'save_load_hashes':a,'window_scene':str(dest/f'md-scenery-{width}.json')}
        print('MD camera',width,'save/load and actual window PASS',flush=True)
    (dest/'state-report.json').write_text(json.dumps({'result':'PASS','widths':result},indent=2)+'\n')

if __name__=='__main__':main()
