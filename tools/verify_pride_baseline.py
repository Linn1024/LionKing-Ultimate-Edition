"""Gate the complete first-level route against the interpreter and native PPU."""
import concurrent.futures
import json
import re
import subprocess
from audit_scenes import ROOT

def main():
    dest=ROOT/'build/pride-baseline';dest.mkdir(parents=True,exist_ok=True)
    def run(mode):
        cmd=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--frames','5000','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
             '--ram-log',str(dest/(mode+'.ram')),'--wide','320']
        if mode=='lle':cmd.append('--lle')
        with (dest/(mode+'.log')).open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        text=(dest/(mode+'.log')).read_text(errors='replace')
        result=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))
        assert len(result)==2,text
        assert re.search(r'\bnative_mismatch=0\b',text),'native compositor differs from PPU in '+mode
        return mode,result
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=dict(pool.map(run,['aot','lle']))
    assert results['aot']==results['lle'],'compiled/interpreter final state differs'
    assert (dest/'aot.ram').read_bytes()==(dest/'lle.ram').read_bytes(),'tracked gameplay differs during the route'
    rows=[x.split() for x in (dest/'aot.ram').read_text().splitlines()]
    transitions=[];prior=None
    for row in rows:
        level=int(row[6],16)
        if level!=prior:transitions.append({'frame':int(row[0]),'level':level});prior=level
    assert any(x['level']==10 for x in transitions),'first-level bonus was not reached'
    assert transitions[-1]['level']==1,'second main level was not reached after the bonus'
    report={'result':'PASS','route_frames':5000,'compiled_interpreter_guest_hashes_equal':True,
            'tracked_ram_equal_every_frame':True,'native_compositor_mismatched_pixels':0,
            'transitions':transitions,'hashes':results['aot']}
    (dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
