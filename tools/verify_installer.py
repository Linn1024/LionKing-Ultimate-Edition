"""Verify ROM import, transactional repair, native cache use and the setup window."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import time
from verify_windows import ROOT,USER32,ENUM,hashes,pixels
from windows_capture import capture_client


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    USER32.SetProcessDPIAware()
    out=ROOT/'build/setup-verification';out.mkdir(parents=True,exist_ok=True)
    data=out/'Game data & cache';cache=data/'scenes-v1.cache'
    snes=ROOT/'Lion King, The (USA).sfc';md=ROOT/'Lion King, The (World).md'
    settings={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()}
    source_hashes={str(p):digest(p) for p in (snes,md)}
    def install(name,a=snes,b=md,expect=0):
        log=out/(name+'.log')
        cmd=['powershell','-NoProfile','-STA','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),
             '-SnesRom',str(a),'-MdRom',str(b),'-DataDirectory',str(data),'-NonInteractive']
        with log.open('wb') as stream:p=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
        assert p.returncode==expect,(name,p.returncode,log.read_text(errors='replace'))
    install('import')
    manifest=data/'install.json';installed=json.loads(manifest.read_text())
    assert installed['original_payloads_retained'] and installed['scene_cache']['decoded_scenes']==12
    assert installed['scene_cache']['verified_background_levels']==[0,2]
    for name,spec in installed['roms'].items():assert digest(data/spec['file'])==spec['sha256'],name
    clean=cache.read_bytes();assert digest(cache)==installed['scene_cache']['sha256']
    install('repeat')
    assert cache.read_bytes()==clean,'Repeated setup changed decoded assets'
    before=manifest.read_bytes()
    install('reject-snes',md,md,1);install('reject-md',snes,snes,1)
    assert manifest.read_bytes()==before and cache.read_bytes()==clean,'Invalid sources changed an existing installation'
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngraphics.scenery = md\ngraphics.sprites.leaves = md\ndisplay.viewport = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    def render(name,cached,expected):
        cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(data/installed['roms']['snes']['file']),
             '--md-rom',str(data/installed['roms']['megadrive']['file']),'--resource-profile',str(profile),
             '--config',str(config),'--frames','1786','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
             '--no-pace','--no-audio','--no-record','--dump-window',str(out/(name+'.png'))]
        if cached:cmd+=['--asset-cache',str(cache)]
        log=out/(name+'.log')
        with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        assert expected in log.read_text(errors='replace'),(name,log.read_text(errors='replace'))
        return hashes(log),pixels(out/(name+'.png'))
    baseline=render('uncached',False,'Saved resource profile loaded')
    assert render('cached',True,'resource_cache=loaded')==baseline,'Cached scenery changed the game or actual window'
    launcher_checked=False
    if (ROOT/'game-data/install.json').exists():
        log=out/'play-launcher.log'
        cmd=['cmd','/d','/c',str(ROOT/'Play.cmd'),'--config',str(config),'--resource-profile',str(profile),
             '--frames','1786','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
             '--no-pace','--no-audio','--no-record','--dump-window',str(out/'play-launcher.png')]
        with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        assert 'resource_cache=loaded' in log.read_text(errors='replace'),'Play.cmd did not use installed data/cache'
        assert (hashes(log),pixels(out/'play-launcher.png'))==baseline,'Installed launcher output differs'
        launcher_checked=True
    failures={}
    for name,mutate in [('damaged-payload',lambda b:b.__setitem__(-1,b[-1]^1)),
                        ('wrong-source',lambda b:b.__setitem__(16,b[16]^1)),
                        ('wrong-version',lambda b:struct.pack_into('<I',b,8,999)),
                        ('oversized',lambda b:struct.pack_into('<I',b,12,0xffffffff))]:
        damaged=bytearray(clean);mutate(damaged);cache.write_bytes(damaged)
        assert render(name,True,'resource_cache=miss_decoded_from_rom')==baseline,name+' changed native fallback'
        failures[name]=True
    install('repair-cache');assert cache.read_bytes()==clean
    # Corrupt only our test-owned imported copy, then verify atomic replacement.
    imported=data/installed['roms']['megadrive']['file'];broken=bytearray(imported.read_bytes());broken[100]^=1;imported.write_bytes(broken)
    install('repair-import');assert digest(imported)==source_hashes[str(md)]
    # Real WinForms UI: operate only the child process' own button HWND.
    gui_log=(out/'gui.log').open('wb')
    process=subprocess.Popen(['powershell','-NoProfile','-STA','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),
                              '-DataDirectory',str(data)],cwd=ROOT,stdout=gui_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    hwnd=None
    try:
        until=time.monotonic()+20
        while process.poll() is None and time.monotonic()<until:
            found=[]
            @ENUM
            def each(handle,unused):
                actual=W.DWORD();USER32.GetWindowThreadProcessId(handle,C.byref(actual))
                title=C.create_unicode_buffer(256);USER32.GetWindowTextW(handle,title,256)
                if actual.value==process.pid and title.value=='Lion King PC Setup':found.append(handle)
                return True
            USER32.EnumWindows(each,0)
            if found:hwnd=found[0];break
            time.sleep(.05)
        assert hwnd,'Setup window did not open'
        time.sleep(.3);capture_client(hwnd,out/'setup-before.png')
        children=[]
        @ENUM
        def child(handle,unused):
            title=C.create_unicode_buffer(512);USER32.GetWindowTextW(handle,title,512)
            children.append((handle,title.value));return True
        USER32.EnumChildWindows.argtypes=[W.HWND,ENUM,W.LPARAM]
        USER32.EnumChildWindows(hwnd,child,0)
        button=next(handle for handle,title in children if title=='Prepare game data')
        USER32.SendMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
        USER32.SendMessageW(button,0xf5,0,0)
        time.sleep(1.5);children.clear();USER32.EnumChildWindows(hwnd,child,0)
        assert any('Ready. Start the game' in title for _,title in children),('Setup UI did not finish',children)
        capture_client(hwnd,out/'setup-ready.png')
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
        gui_log.close()
    assert source_hashes=={str(p):digest(p) for p in (snes,md)},'Setup altered source ROMs'
    assert settings=={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()},'Setup altered existing settings or saves'
    report={'result':'PASS','all_original_bytes_imported':True,'repeatable':True,'invalid_sources_rejected_before_mutation':True,
            'cache_and_uncached_guest_and_actual_window_identical':True,'fallbacks':failures,
            'cache_and_import_repair':True,'actual_setup_window':True,'source_roms_settings_and_saves_unchanged':True,
            'installed_play_launcher_checked':launcher_checked,
            'cache_bytes':len(clean),'source_hashes':source_hashes}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Setup import, cache use/fallback/repair, unchanged user data and actual Windows UI PASS',flush=True)


if __name__=='__main__':main()
