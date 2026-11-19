"""Exercise actual installer bank5 publication, repeat, locked-target failure and preservation."""
import ctypes as C
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-title-bank-installed';out=base/'setup-verification';out.mkdir()
    data=out/'Game data & title bank';checks={};commands={}
    settings={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()}
    snes=ROOT/'Lion King, The (USA).sfc';md=ROOT/'Lion King, The (World).md'
    before={p:digest(p) for p in (snes,md)}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    def setup(name,a=snes,b=md):
        cmd=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-SnesRom',str(a),'-MdRom',str(b),'-DataDirectory',str(data),'-NonInteractive']
        commands[name]=cmd
        with (out/(name+'.log')).open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        return result.returncode
    checks['actual_install']=setup('install')==0
    manifest=data/'install.json';first=json.loads(manifest.read_text())
    native=data/first['native_final_assets']['file'];menu=data/first['menu_assets']['file']
    raw=native.read_bytes();menu_raw=menu.read_bytes();title=data/first['title_bank_assets']['file'];title_raw=title.read_bytes()
    checks['title_manifest']=first['title_bank_assets']['version']==1 and first['title_bank_assets']['bank']==5 and first['title_bank_assets']['packets']==16 and first['title_bank_assets']['source']=='snes'
    checks['title_component_bytes']=title_raw==(base/'title-bank.assets').read_bytes() and len(title_raw)==53826
    checks['title_digest']=digest(title)==first['title_bank_assets']['sha256']
    checks['native_manifest']=first['native_final_assets']['payloads']==20 and first['native_final_assets']['version']==2 and first['native_final_assets']['source']=='snes'
    checks['native_digest']=digest(native)==first['native_final_assets']['sha256']
    checks['native_preparation_matches_component']=raw==(base/'verification/native.assets').read_bytes()
    checks['native_portable_record']=len(raw)==200724 and raw[:8]==b'TLKFNAT1'
    checks['menu_unchanged']=digest(menu)=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    checks['scene_cache_preserved']=digest(data/first['scene_cache']['file'])==first['scene_cache']['sha256']
    checks['repeat_succeeds']=setup('repeat')==0
    second=json.loads(manifest.read_text())
    checks['repeat_same_packages']=second['title_bank_assets']==first['title_bank_assets'] and title.read_bytes()==title_raw and second['native_final_assets']==first['native_final_assets'] and second['menu_assets']==first['menu_assets'] and native.read_bytes()==raw and menu.read_bytes()==menu_raw
    # An exclusive Windows handle blocks replacement of this package after the
    # helper has prepared its new staged file. Earlier referenced data survives.
    kernel=C.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[C.c_wchar_p,C.c_ulong,C.c_ulong,C.c_void_p,C.c_ulong,C.c_ulong,C.c_void_p];kernel.CreateFileW.restype=C.c_void_p
    kernel.CloseHandle.argtypes=[C.c_void_p]
    handle=kernel.CreateFileW(str(title),0x80000000,0,None,3,0x80,None);assert handle not in (None,C.c_void_p(-1).value)
    previous_manifest=manifest.read_bytes()
    try:checks['title_publication_failure_rejects']=setup('locked-title')!=0
    finally:kernel.CloseHandle(handle)
    checks['title_failure_preserves_manifest']=manifest.read_bytes()==previous_manifest
    checks['title_failure_preserves_packages']=native.read_bytes()==raw and menu.read_bytes()==menu_raw and title.read_bytes()==title_raw
    checks['retry_after_unlock']=setup('retry')==0
    previous_manifest=manifest.read_bytes()
    checks['wrong_source_rejects']=setup('wrong-source',snes,snes)!=0
    checks['wrong_source_preserves_manifest']=manifest.read_bytes()==previous_manifest
    checks['no_partial_packages']=not any('.staging' in p.name or '.install-part' in p.name for p in data.rglob('*'))
    checks['settings_preserved']=all(digest(ROOT/p)==sha for p,sha in settings.items())
    checks['original_roms_preserved']=all(digest(p)==sha for p,sha in before.items())
    paths=[Path(__file__),ROOT/'scripts/Setup.ps1',ROOT/'engine/tools/prepare_final_assets.c',ROOT/'engine/cmake/TlkFinalAssets.cmake',ROOT/'dist/PrepareFinalAssets.exe']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
