"""Check camera adapter execution, interpreter parity and viewport bounds."""
import csv
import json
import os
import re
import subprocess
from audit_scenes import ROOT

def main():
    dest=ROOT/'build/pride-camera-verification';dest.mkdir(parents=True,exist_ok=True)
    results={}
    for width in (256,320):
        profile=dest/f'{width}.ini'
        profile.write_text('schema = 1\ngame = snes\ngameplay.camera = md\n'+
                           ('display.viewport = md\n' if width==320 else ''))
        modes={}
        for mode in ('aot','lle'):
            stem=dest/f'{width}-{mode}'
            env=os.environ.copy();env['TLK_CAMERA_TRACE']=str(stem)+'.csv'
            command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                     '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                     '--frames','5000','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
                     '--wide',str(width),'--wide-png',str(stem)+'.png','--ram-log',str(stem)+'.ram']
            if mode=='lle':command+=['--lle']
            with stem.with_suffix('.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            text=stem.with_suffix('.log').read_text(errors='replace')
            hashes=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))
            assert len(hashes)==2,text
            rows=list(csv.DictReader(stem.with_suffix('.csv').open()))
            assert len(rows)>500,'camera adapter did not execute'
            moving=[r for r in rows if r['frozen']=='0']
            assert all(0<=int(r['x'])<=1600-width and 16<=int(r['y'])<=1056 for r in moving),'camera escaped level bounds'
            assert max(int(r['x']) for r in rows)>400,'replay did not exercise scrolling'
            modes[mode]={'hashes':hashes,'updates':len(rows),'max_x':max(int(r['x']) for r in rows)}
        assert modes['aot']==modes['lle'],'camera AOT/LLE hashes or updates differ'
        for suffix in ('.ram','.csv'):
            assert (dest/f'{width}-aot{suffix}').read_bytes()==(dest/f'{width}-lle{suffix}').read_bytes(),'camera route differs '+suffix
        results[str(width)]=modes['aot'];print('MD camera',width,'AOT/LLE PASS',flush=True)
    (dest/'report.json').write_text(json.dumps({'result':'PASS','widths':results},indent=2)+'\n')

if __name__=='__main__':main()
