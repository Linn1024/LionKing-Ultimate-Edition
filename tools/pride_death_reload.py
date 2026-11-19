"""Observe native post-death reload fields with all independent music choices."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-death-reload';out.mkdir(exist_ok=True)
    path=out/'report.json';path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    source=ROOT/'build/pride-death-phases'
    earlier=json.loads((source/'report.json').read_text());assert earlier['result']=='PASS'
    binary=ROOT/'engine/build-win/tlk_headless.exe';identity=digest(binary)
    assert earlier['headless_sha256']==identity
    tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape';runs={}
    for name,previous in earlier['runs'].items():
        modes={}
        for mode in ('aot','lle'):
            folder=out/(name+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_WRAM_DIR']=str(folder)
            env['TLK_WRAM_DUMP']=','.join(map(str,range(4901,5401)))
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',source/(name+'.ini'),'--frames','5400','--input-polled',tape,'--ram-log',folder/'route.ram']
            if name=='native' and mode=='aot':cmd+=['--dump-png',folder/'picture.png','--dump-every','10']
            if mode=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            current={'guest':hashes(folder/'run.log'),'tracked_sha256':digest(folder/'route.ram')}
            assert all(current[k]==previous[k] for k in current),name
            current['sampled_wram_hashes']=[digest(folder/f'hl_wram_{f}.bin') for f in range(4901,5401)]
            modes[mode]=current
        assert modes['aot']==modes['lle'],name
        runs[name]=modes['aot'];print(name,'post-death reload500 full WRAM fields AOT/LLE PASS',flush=True)
    assert digest(binary)==identity
    result={'result':'PASS','scope':__doc__,'headless_sha256':identity,'ordinary_power_on_runs':8,
            'runs':runs,'post_death_sampled_fields_per_source':500,'loaded_states':False,'guest_edits':False,
            'source_sha256':{'script':digest(Path(__file__)),'input':digest(tape),'earlier':digest(source/'report.json')}}
    path.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
