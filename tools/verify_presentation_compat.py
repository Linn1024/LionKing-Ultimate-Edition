"""Keep Pride presentation schema1 readable after scene ownership was added."""
import json,struct,subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    source=ROOT/'build/pride-presentation-state';out=ROOT/'build/presentation-schema-compat';out.mkdir(parents=True,exist_ok=True)
    raw=bytearray((source/'1848-mixed.state').read_bytes());at=36+struct.unpack_from('<Q',raw,24)[0];n=struct.unpack_from('<I',raw,at)[0];view=bytearray(raw[at+4:at+4+n])
    assert struct.unpack_from('<I',view,8)[0]==2 and struct.unpack_from('<i',view,48)[0]==0
    struct.pack_into('<I',view,8,1);view=view[:48]+view[52:]
    struct.pack_into('<I',raw,8,3)
    legacy=out/'schema1.state';legacy.write_bytes(raw[:at]+struct.pack('<I',len(view))+view)
    cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(source/'mixed.ini'),'--config',str(source/'host.ini'),
         '--load',str(legacy),'--input-polled',str(source/'1848-mixed.polled.tape'),'--frames','1849','--no-pace','--no-audio','--no-record','--dump-window',str(out/'window.png'),'--dump-scene',str(out/'scene.json')]
    log=out/'game.log'
    with log.open('wb') as f:subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
    assert hashes(log)==hashes(source/'1848-continuous.log') and pixels(out/'window.png')==pixels(source/'1848-continuous.png')
    assert json.loads((out/'scene.json').read_text())==json.loads((source/'1848-continuous.json').read_text())
    (out/'report.json').write_text(json.dumps({'result':'PASS','legacy_presentation_schema':1,'current_presentation_schema':2,'first_loaded_window_scene_and_guest_identical':True},indent=2)+'\n')
    print('Legacy Pride presentation schema1 first loaded window identical PASS',flush=True)


if __name__=='__main__':main()
