"""Verify native per-letter motion under independent caption source choices."""
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels,hashes
from pride_sprite_catalog import bitmap


def main():
    base=ROOT/'build/pride-title-work';out=base/'entrance3';out.mkdir()
    bp=base/'final-build3.json';build=json.loads(bp.read_text())
    binary=base/'player/native-engine/tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    parent=base/'player-check3';config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    snes=(ROOT/'Lion King, The (USA).sfc').read_bytes();md=(ROOT/'Lion King, The (World).md').read_bytes()
    md_palette=[sum(((c>>s&7)*4+((c>>s&7)>>2))<<(n*5) for n,s in enumerate((1,5,9))) for c in struct.unpack_from('>16H',md,0x1d78aa)]
    checks={};observations=[];commands=[]
    for width in (256,320):
        for field in (950,964):
            reference=parent/f'{width}-{field}-native';scene=json.loads((reference/'scene.json').read_text())
            pw,ph,original=pixels(reference/'window.png');parts=[p for p in scene['pieces'] if p['title_owner']]
            assert len(parts)==13
            # Caption follows the original camera. Infer its actual viewport
            # column from the native raster rather than assuming a centred view.
            native_points=[];position_points=[]
            for p in parts:
                cell=p['local'][0]//16;character=snes[0x3bc97+cell];source=0x2888ef+(character-65)*128
                ox,oy,w,h,data=bitmap(snes,[(0,0,16,16,source)],False,with_origin=True)
                for i,c in enumerate(data):
                    if not c:continue
                    if p['kept']:native_points.append((p['screen'][0]+ox+i%w,p['screen'][1]+oy+i//w,c))
                    position_points.append((width//2-112+p['local'][0]+ox+i%w,72+p['local'][1]+oy+i//w,c))
            native_palette=scene['obj_palette0']
            hud_boxes=[]
            for p in scene['pieces']:
                if not p['fixed'] or not p['kept']:continue
                shift=width-256 if p['screen'][0]>=128 else 0
                x,y=p['screen'];hud_boxes.append((x+shift,y,x+shift+p['size'],y+p['size']))
            def hud(x,y):return any(a<=x<c and b<=y<d for a,b,c,d in hud_boxes)
            def rgb(c,y,palette):
                bright=scene['lines'][y]['brightness'];value=palette[c]
                return tuple((((value>>s&31)<<3)|((value>>s&31)>>2))*bright//15 for s in (0,5,10))
            columns=[]
            for column in range(width-256+1):
                if all(original[(y*3+1)*pw+(x+column)*3+1]==rgb(c,y,native_palette) or hud(x+column,y)
                       for x,y,c in native_points if 0<=x+column<width and 0<=y<224):columns.append(column)
            assert len(columns)==1,(width,field,columns)
            column=columns[0]
            for choice in ('duration','palette','position'):
                folder=out/f'{width}-{field}-{choice}';folder.mkdir();profile=folder/'resources.ini'
                profile.write_text('schema = 1\ngame = snes\n'+('display.viewport = md\n' if width==320 else '')+
                    f'graphics.titles.pride_lands.{choice} = md\n')
                cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                     '--config',config,'--resource-profile',profile,'--load',parent/'before-caption.state',
                     '--input-polled',parent/'after930.polled.tape','--frames',field,'--no-pace','--no-audio','--no-record',
                     '--dump-window',folder/'window.png']
                commands.append(list(map(str,cmd)))
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(commands[-1],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
                _,_,actual=pixels(folder/'window.png');label=f'{width}/{field}/{choice}'
                checks[label+'/guest_unchanged']=hashes(folder/'run.log')==hashes(reference/'run.log')
                if choice=='duration':checks[label+'/native_entrance_exact']=actual==original
                else:
                    points=position_points if choice=='position' else [(x+column,y,c) for x,y,c in native_points]
                    palette=native_palette if choice=='position' else md_palette
                    # The repositioned wide HUD can legitimately occlude the
                    # falling letters. Do not demand font colours through it.
                    checks[label+'/native_letter_motion_preserved']=all(actual[(y*3+1)*pw+x*3+1]==rgb(c,y,palette)
                        for x,y,c in points if 0<=x<width and 0<=y<224 and not hud(x,y))
                observations.append(dict(width=width,field=field,choice=choice,inferred_native_column=column))
            print(width,field,'native entrance / independent palette / anchor checked',flush=True)
    paths=[Path(__file__),bp,parent/'report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'entrance checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
