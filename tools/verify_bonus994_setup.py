"""Actual isolated Setup with coherent scene-v3, final actor package and existing HUD."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus994-setup';out.mkdir(exist_ok=True);helper=ROOT/'build/bonus985-sprite-helper/build-report.json';scene=ROOT/'build/hakuna787-helper/build-report.json';h=bound(helper);s=bound(scene);bound(ROOT/'build/bonus989/build-report.json');ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-SnesRom',str(ROOT/'Lion King, The (USA).sfc'),'-MdRom',str(ROOT/'Lion King, The (World).md'),'-DataDirectory',str(out/'data'),'-SpritePreparer',str(helper.parent/'build/PrepareSpriteAssets.exe'),'-ScenePreparer',str(scene.parent/'build/PrepareSceneAssets.exe')]
with (out/'setup.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=65,creationflags=subprocess.CREATE_NO_WINDOW)
m=json.loads((out/'data/install.json').read_text(encoding='utf-8-sig'));old=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'));keys=[k for k,v in old.items() if isinstance(v,dict) and k not in ('sprite_assets','scene_cache')]
checks=dict(sprite_native_output=m['sprite_assets']['sha256']==h['cache_sha256'] and m['sprite_assets']['mapped_images']==1466,scene_native_output=m['scene_cache']['sha256']==s['cache_sha256'] and m['scene_cache']['version']==3,accurate_background_scope=m['scene_cache']['verified_background_levels']==[0,1,2,4,5,6,7,8,9,10,11,12,13],other_payloads_preserved=all(m[k].get('sha256')==old[k].get('sha256') if k!='roms' else m[k]==old[k] for k in keys),hud_package_unchanged=m['hud_assets']['sha256']==old['hud_assets']['sha256'])
paths=[Path(__file__),helper,scene,ROOT/'build/bonus989/build-report.json',ROOT/'scripts/Setup.ps1',out/'data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
