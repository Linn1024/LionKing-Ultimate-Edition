"""Check that the shortened caption does not flash back at native retirement."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels
from pride_sprite_catalog import bitmap


def main():
    base=ROOT/'build/pride-title-work';out=base/'retirement';out.mkdir()
    bp=base/'final-build3.json';build=json.loads(bp.read_text())
    binary=base/'player/native-engine/tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    parent=base/'player-check3';config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngraphics.titles.pride_lands = md\n')
    snes=(ROOT/'Lion King, The (USA).sfc').read_bytes();checks={};observations=[];commands=[]
    for field in range(1088,1101):
        folder=out/str(field);folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--load',parent/'before-caption.state',
             '--input-polled',parent/'after930.polled.tape','--frames',field,'--no-pace','--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))},
                           stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        scene=json.loads((folder/'scene.json').read_text());w,h,image=pixels(folder/'window.png')
        parts=[p for p in scene['pieces'] if p['pose']==0x7e17dd and p['kept']]
        matches=tested=0
        for p in parts:
            cell=p['local'][0]//16
            if not 0<=cell<14 or cell==3:continue
            character=snes[0x3bc97+cell]
            ox,oy,gw,gh,data=bitmap(snes,[(0,0,16,16,0x2888ef+(character-65)*128)],False,with_origin=True)
            for i,c in enumerate(data):
                if not c:continue
                x=p['screen'][0]+ox+i%gw;y=p['screen'][1]+oy+i//gw
                if not 0<=x<256 or not 0<=y<224:continue
                color=scene['obj_palette0'][c];bright=scene['lines'][y]['brightness']
                expected=tuple((((color>>s&31)<<3)|((color>>s&31)>>2))*bright//15 for s in (0,5,10))
                tested+=1;matches+=image[(y*3+1)*w+x*3+1]==expected
        checks[str(field)+'/no_native_caption_flash']=not tested or matches<tested
        observations.append(dict(field=field,latched_font_pieces=len(parts),owned=sum(bool(p['title_owner']) for p in parts),
                                 native_opaque_pixels=tested,native_colour_matches=matches))
        print(observations[-1],flush=True)
    paths=[Path(__file__),bp,parent/'report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'retirement window checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
