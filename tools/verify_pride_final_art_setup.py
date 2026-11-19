"""Exercise actual Setup menu preparation, repeat and invalid-source preservation."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-final-art-setup';out=base/'verification';out.mkdir()
    data=out/'Game data & menus';checks={};commands={}
    settings={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    snes=ROOT/'Lion King, The (USA).sfc';md=ROOT/'Lion King, The (World).md'
    before_sources={str(p):digest(p) for p in (snes,md)}
    def setup(name,a=snes,b=md):
        cmd=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),
            '-SnesRom',str(a),'-MdRom',str(b),'-DataDirectory',str(data),'-NonInteractive']
        commands[name]=cmd
        with (out/(name+'.log')).open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        return result.returncode
    checks['actual_setup_succeeds']=setup('install')==0
    manifest=data/'install.json';first=json.loads(manifest.read_text());menu=data/first['menu_assets']['file']
    checks['manifest_menu_digest']=digest(menu)==first['menu_assets']['sha256']
    checks['retained_scene_cache']=digest(data/first['scene_cache']['file'])==first['scene_cache']['sha256']
    raw=menu.read_bytes();checks['default_inventory37']=int.from_bytes(raw[20:24],'little')==37
    checks['repeat_succeeds']=setup('repeat')==0
    second=json.loads(manifest.read_text());checks['repeat_identical_package']=menu.read_bytes()==raw and second['menu_assets']==first['menu_assets']
    old_manifest=manifest.read_bytes()
    checks['invalid_sources_rejected']=setup('invalid',snes,snes)!=0
    checks['invalid_preserves_installation']=manifest.read_bytes()==old_manifest and menu.read_bytes()==raw
    checks['no_staging_files']=not list(data.glob('*.staging')) and not list(data.glob('*.install-part'))
    cmd=[str(ROOT/'dist/PrepareFinalAssets.exe'),'--md-rom',str(snes),'--output',str(menu)];commands['bad-preparer']=cmd
    with (out/'bad-preparer.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=60)
    checks['bad_preparer_source_rejected']=r.returncode==4
    checks['bad_preparer_preserves_package']=menu.read_bytes()==raw
    cmd=[str(ROOT/'.tools/python32/python.exe'),str(ROOT/'tools/verify_pride_final_art_inventory.py'),str(menu),str(out/'inventory')]
    commands['reader_inventory']=cmd
    with (out/'inventory.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    checks['decoder_free_reader_inventory']=r.returncode==0
    checks['settings_preserved']=all(digest(ROOT/p)==s for p,s in settings.items())
    checks['source_roms_preserved']=all(digest(Path(p))==s for p,s in before_sources.items())
    paths=[Path(__file__),ROOT/'scripts/Setup.ps1',ROOT/'scripts/Build.ps1',ROOT/'engine/CMakeLists.txt',
        ROOT/'engine/cmake/TlkFinalAssets.cmake',ROOT/'engine/tools/final-assets/CMakeLists.txt',
        ROOT/'engine/tools/prepare_final_assets.c',ROOT/'engine/runner/tlk_final_art_prepare.c',ROOT/'engine/runner/tlk_final_art_prepare.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        binary_sha256=digest(ROOT/'dist/PrepareFinalAssets.exe'),
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
