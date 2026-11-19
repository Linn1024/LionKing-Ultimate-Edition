"""Check added SNES-background margins while preserving the original PPU view."""
import json
import re
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    out=ROOT/'build/pride-native-edges';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\nwidescreen_hud = in place\n')
    captures={};guest={}
    for name,extra in [('native',''),('wide','display.viewport = md\n')]:
        profile=out/(name+'.ini');profile.write_text('schema = 1\ngame = snes\n'+extra)
        command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
                 '--resource-profile',str(profile),'--frames','1786',
                 '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--no-pace','--no-audio',
                 '--no-record','--dump-window',str(out/(name+'.png')),'--dump-scene',str(out/(name+'.json'))]
        log=out/(name+'.log')
        with log.open('wb') as stream:
            subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        guest[name]=hashes(log);captures[name]=pixels(out/(name+'.png'))
    assert guest['native']==guest['wide'],'Viewport changed guest state'
    nw,nh,native=captures['native'];ww,wh,wide=captures['wide']
    assert (nw,nh,ww,wh)==(768,672,960,672)
    for y in range(nh):
        assert native[y*nw:(y+1)*nw]==wide[y*ww+96:y*ww+96+nw],'Original PPU columns changed'
    scene=json.loads((out/'wide.json').read_text());row=scene['lines'][120]
    assert scene['stage_detected'] and scene['level']==0 and row['bgsc'][1]&3==1
    scroll=row['scroll'][1][0]&1023
    assert scroll==26,'Regression fixture no longer exposes the negative six-column margin'
    # This sampled sky/horizon area has no foreground, actors or moved HUD.
    # The six unavailable columns must extend background source column zero.
    for y in range(120*3,170*3):
        assert all(wide[y*ww+x]==wide[y*ww+18] for x in range(18)),'Far-right map strip wrapped into the added left edge'
    log=out/'complete-native.log'
    command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--frames','5000','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--wide','320']
    with log.open('wb') as stream:
        subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
    assert re.search(r'\bnative_mismatch=0\b',log.read_text()),'Native centre mismatches appeared during the route'
    report={'result':'PASS','original_256_columns_unchanged':True,'extended_missing_columns':6,
            'complete_route_native_pixel_mismatches':0,'guest_hashes':guest['native']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('SNES Pride background: added edge fixed, original columns and full-route native pixels unchanged PASS',flush=True)


if __name__=='__main__':main()
