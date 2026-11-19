"""Check Stampede's verified MD H32 viewport and preserve explicit wide views."""
import json,re,struct,subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    out=ROOT/'build/stampede-viewport';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\naspect = 4:3\n')
    profiles={}
    for name,extra in [('snes',''),('md','display.viewport = md\n'),('md-camera','display.viewport = md\ngameplay.camera = md\n')]:
        p=out/(name+'.ini');p.write_text('schema = 1\ngame = snes\n'+extra);profiles[name]=p
    base=['--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md')]
    sdl=ROOT/'dist/LionKing.exe';head=ROOT/'engine/build-win/tlk_headless.exe';state=out/'level.state'
    def run(name,host,source,end,extra):
        log=out/(name+'.log');cmd=[str(host),*base,'--resource-profile',str(profiles[source]),'--frames',str(end),*map(str,extra)]
        if host==sdl:cmd+=['--config',str(config),'--no-pace','--no-audio','--no-record']
        with log.open('wb') as f:subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        return hashes(log)
    run('prepare',sdl,'snes',2300,['--practice-level','3','--save-at','2300',state])
    results={}
    for source in ('snes','md','md-camera'):
        save=out/(source+'.state')
        results[source]=run(source,sdl,source,2310,['--load',state,'--save-at','2310',save,'--dump-window',out/(source+'.png'),'--dump-scene',out/(source+'.json')])
        scene=json.loads((out/(source+'.json')).read_text());assert scene['level']==3 and not scene['stage_detected'],'Wrong special-scene fixture'
    assert results['snes']==results['md']==results['md-camera'],'Viewport or inactive camera source changed gameplay'
    assert pixels(out/'snes.png')==pixels(out/'md.png')==pixels(out/'md-camera.png'),'Automatic H32 leaves incorrect CRT padding'
    flags=struct.unpack_from('<I',(out/'md-camera.state').read_bytes(),32)[0]
    assert flags&1 and (flags>>8)&65535==320,'Stage viewport overwrote the future Pride gameplay-camera width'
    value=run('headless-md',head,'md',2310,['--load',state,'--dump-png',out/'stock.png','--wide-png',out/'auto.png'])
    assert value==results['snes'] and pixels(out/'auto.png')==pixels(out/'stock.png') and pixels(out/'auto.png')[:2]==(256,224)
    spawn=run('headless-auto-spawn',head,'md',2310,['--load',state,'--wide-spawn'])
    assert spawn==value,'A native-width automatic view retained the wider spawn margin'
    explicit=run('headless-explicit',head,'md',2310,['--load',state,'--wide','320','--wide-png',out/'explicit.png'])
    assert explicit==value and pixels(out/'explicit.png')[:2]==(320,224),'Explicit widescreen was overridden'
    # The previous level retains its independently verified 320-column mode.
    report={'result':'PASS','scene':3,'native_md_video_width':256,'explicit_wide_override_width':320,'crt_window_matches_native':True,'pride_gameplay_camera_width_retained':320,'guest_hashes':results}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Stampede automatic MD256 viewport, CRT aspect, explicit wide override and guest isolation PASS',flush=True)


if __name__=='__main__':main()
