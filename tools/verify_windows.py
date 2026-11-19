"""Exercise the real Windows game window, presentation, and live F10 switching.

Uses only the standard library. Captures and temporary profiles stay in build/.
"""
import ctypes as C
from ctypes import wintypes as W
from pathlib import Path
import json
import re
import struct
import subprocess
import time
import zlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/windows-smoke'
EXE=ROOT/'engine/build-win/tlk_sdl.exe'
SNES=next(ROOT.glob('*.sfc'))
MD=ROOT/'Lion King, The (World).md'
USER32=C.WinDLL('user32',use_last_error=True)
USER32.GetWindowThreadProcessId.argtypes=[W.HWND,C.POINTER(W.DWORD)]
USER32.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
USER32.PostMessageW.restype=W.BOOL
ENUM=C.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM)
USER32.EnumWindows.argtypes=[ENUM,W.LPARAM]
USER32.GetWindowTextW.argtypes=[W.HWND,W.LPWSTR,C.c_int]

def window_for(pid):
    found=[]
    @ENUM
    def each(hwnd,unused):
        actual=W.DWORD()
        USER32.GetWindowThreadProcessId(hwnd,C.byref(actual))
        if actual.value==pid:
            title=C.create_unicode_buffer(256)
            USER32.GetWindowTextW(hwnd,title,256)
            if title.value=='The Lion King': found.append(hwnd)
        return True
    USER32.EnumWindows(each,0)
    return found[0] if found else None

def hashes(log):
    text=log.read_text(errors='replace')
    return dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))

def run(name,extra=(),key=None):
    log=OUT/f'{name}.log'
    cmd=[str(EXE),'--rom',str(SNES),'--md-rom',str(MD),'--config',str(OUT/'host.ini'),
         '--resource-profile',str(OUT/'resources.ini'),'--no-audio','--no-record',*map(str,extra)]
    with log.open('wb') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            if key:
                until=time.monotonic()+5
                hwnd=None
                while p.poll() is None and time.monotonic()<until:
                    hwnd=window_for(p.pid)
                    if hwnd: break
                    time.sleep(.02)
                assert hwnd, 'game window not found'
                time.sleep(.25)
                assert USER32.PostMessageW(hwnd,0x100,key,1), 'key down failed'
                assert USER32.PostMessageW(hwnd,0x101,key,0xc0000001), 'key up failed'
            p.wait(timeout=35)
            assert p.returncode==0, f'{name} exit {p.returncode}; see {log}'
        finally:
            if p.poll() is None: p.terminate(); p.wait(timeout=5)
    return hashes(log)

def pixels(path):
    data=path.read_bytes(); pos=8; compressed=bytearray(); w=h=0
    while pos<len(data):
        size=int.from_bytes(data[pos:pos+4],'big'); kind=data[pos+4:pos+8]; chunk=data[pos+8:pos+8+size]
        if kind==b'IHDR':
            w,h=struct.unpack_from('>II',chunk)
            assert chunk[8:10]==bytes((8,2))
        if kind==b'IDAT': compressed.extend(chunk)
        pos+=size+12
    raw=zlib.decompress(compressed); stride=w*3+1
    assert len(raw)==stride*h
    assert all(raw[y*stride]==0 for y in range(h))
    return w,h,[tuple(raw[y*stride+1+x*3:y*stride+4+x*3]) for y in range(h) for x in range(w)]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'host.ini').write_text('opengl = 1\nscale = 3\n')
    profile=OUT/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\n')
    state=OUT/'level.state'
    # Save twice to the same Windows path to verify slot replacement as well.
    for n in range(2):
        run(f'prepare-{n}',['--practice-level','0','--frames','2200','--no-pace','--save-at','2200',state])
    common=['--load',state,'--frames','2210','--no-pace']
    stock=run('stock',common+['--dump-window',OUT/'stock.png','--dump-png',OUT/'guest-stock.png'])
    profile.write_text('schema = 1\ngame = snes\ngraphics.sprites.simba.cub.palette = md\n')
    mixed=run('mixed',common+['--dump-window',OUT/'mixed.png','--dump-png',OUT/'guest-mixed.png'])
    assert stock==mixed and len(stock)==2, 'asset choice changed guest frame/RAM'
    assert (OUT/'guest-stock.png').read_bytes()==(OUT/'guest-mixed.png').read_bytes()
    w,h,a=pixels(OUT/'stock.png'); mw,mh,b=pixels(OUT/'mixed.png')
    assert (w,h)==(mw,mh)==(768,672)
    changed=[(i%w,i//w) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert changed, 'mixed palette did not change presentation'
    bbox=[min(x for x,y in changed),min(y for x,y in changed),max(x for x,y in changed)+1,max(y for x,y in changed)+1]
    assert 100<=bbox[0]<bbox[2]<=300 and 450<=bbox[1]<bbox[3]<=620, f'changes escaped Simba: {bbox}'
    profile.write_text('schema = 1\ngame = snes\ngraphics.hud.palette = md\n')
    hud=run('hud-palette',common+['--dump-window',OUT/'hud-palette.png'])
    assert hud==stock,'HUD palette changed guest state'
    hw,hh,hp=pixels(OUT/'hud-palette.png');assert (hw,hh)==(w,h)
    hud_changed=[(i%w,i//w) for i,(x,y) in enumerate(zip(a,hp)) if x!=y]
    assert hud_changed,'HUD palette adapter was invisible'
    assert all(y<300 or (x<150 and y>525) for x,y in hud_changed),'HUD palette changed a world actor'
    assert not any(original!=hud_pixel and original!=cub_pixel for original,hud_pixel,cub_pixel in zip(a,hp,b)), 'HUD palette recoloured Simba'
    profile.write_text('schema = 1\ngame = snes\ngraphics.scenery = md\ndisplay.viewport = md\n')
    scenery=run('scenery',common+['--dump-window',OUT/'scenery.png','--dump-png',OUT/'guest-scenery.png'])
    assert scenery==stock, 'scenery/viewport choices changed game state'
    assert (OUT/'guest-stock.png').read_bytes()==(OUT/'guest-scenery.png').read_bytes()
    sw,sh,scene_pixels=pixels(OUT/'scenery.png')
    assert (sw,sh)==(960,672), f'MD viewport size is wrong: {(sw,sh)}'
    for feature in ('foreground','background','palettes'):
        profile.write_text('schema = 1\ngame = snes\ngraphics.scenery.'+feature+' = md\n')
        result=run('only-'+feature,common+['--dump-window',OUT/('only-'+feature+'.png')])
        assert result==stock, feature+' changed guest state'
        fw,fh,fp=pixels(OUT/('only-'+feature+'.png'))
        assert (fw,fh)==(768,672)
        assert any(x!=y for x,y in zip(fp,a)), feature+' did not change the presentation'
    profile.write_text('schema = 1\ngame = snes\n')
    run('tree',common+['--menu-at','2210','--menu-page','resources','--dump-window',OUT/'tree.png'])
    profile.write_text('schema = 1\ngame = snes\n')
    live=['--load',state,'--frames','2280']
    first=run('live-to-md',live,key=0x79)
    assert 'graphics.sprites.simba.cub.palette = md' in profile.read_text(), 'F10 failed to select MD'
    second=run('live-to-snes',live,key=0x79)
    assert 'graphics.sprites.simba.cub.palette = snes' in profile.read_text(), 'F10 failed to restore SNES'
    assert first==second, 'live switch changed guest state'
    adult={}; adult_pixels={}
    for source in ('snes','md'):
        profile.write_text('schema = 1\ngame = snes\ngraphics.sprites.simba.adult.palette = '+source+'\n')
        adult[source]=run('adult-'+source,['--practice-level','6','--frames','2300','--no-pace',
                                        '--dump-window',OUT/('adult-'+source+'.png')])
        adult_pixels[source]=pixels(OUT/('adult-'+source+'.png'))
    assert adult['snes']==adult['md'], 'adult palette changed guest state'
    assert adult_pixels['snes'][:2]==adult_pixels['md'][:2]
    assert adult_pixels['snes'][2]!=adult_pixels['md'][2], 'adult palette had no visible effect'
    profile.write_text('schema = 1\ngame = snes\ngraphics.scenery = md\ndisplay.viewport = md\n')
    run('panorama-left-edge',['--input-polled',ROOT/'engine/tapes/allbugsF.read.tape',
                             '--frames','985','--no-pace','--dump-window',OUT/'panorama-left-edge.png'])
    pw,ph,panorama=pixels(OUT/'panorama-left-edge.png')
    assert (pw,ph)==(960,672)
    # At this replay camera position the sky reaches the left edge. Previously
    # the first 36 window pixels showed purple terrain from the panorama's end.
    sky=panorama[300*pw+100]
    assert sky==(239,239,206), 'reference sky sample changed'
    assert all(panorama[300*pw+x]==sky for x in range(36)), 'panorama wrapped into the left margin'
    fallback={}; fallback_pixels={}
    for source in ('snes','md'):
        profile.write_text('schema = 1\ngame = snes\ngraphics.scenery.background = '+source+'\n')
        fallback[source]=run('hakuna-bg-'+source,['--practice-level','5','--frames','2300','--no-pace',
                                                '--dump-window',OUT/('hakuna-bg-'+source+'.png')])
        fallback_pixels[source]=pixels(OUT/('hakuna-bg-'+source+'.png'))
    assert fallback['snes']==fallback['md'], 'background fallback changed guest state'
    assert fallback_pixels['snes']==fallback_pixels['md'], 'unadapted MD background bypassed native fallback'
    report={'result':'PASS','guest_hashes':stock,'presentation_changed_pixels':len(changed),
            'presentation_change_bbox':bbox,'live_F10_round_trip':True,'save_slot_overwrite':True,
            'resource_tree_capture':str(OUT/'tree.png'), 'md_viewport':[320,224],
            'scenery_sources_independent':True,'scenery_guest_state_unchanged':True,
            'adult_palette_visible_and_guest_unchanged':True,'panorama_left_edge_no_wrap':True,
            'hud_palette_independent_of_simba':True,
            'unadapted_background_native_fallback':True}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
