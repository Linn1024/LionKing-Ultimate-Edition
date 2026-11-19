"""Upgrade caption installation and select the prepared-data player atomically."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-caption277-installed';bp=base/'build-report.json';b=bound(bp)
package=ROOT/'dist/installed-preview277/package-report.json';bound(package)
proof=ROOT/'build/pride-caption282-window/report.json';r=bound(proof);assert r['result']=='PASS' and all(r['checks'].values())
archive=ROOT/'build/pride-caption283-baseline';archive.mkdir();records={}
for name in ('game-data/install.json','scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/installation.md','docs/pride-title-art.md','docs/launchers.md','docs/background-audit.md','README.md','engine/docs/devlog.md'):
    p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(archive/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
history=ROOT/'tools/pride_arena_history.py';text=history.read_text();anchor="    folders.append('pride-caption275-baseline')";assert text.count(anchor)==1
history.write_text(text.replace(anchor,anchor+"\n    folders.append('pride-caption283-baseline')"))
manifest=ROOT/'game-data/install.json';old=json.loads(manifest.read_text())
protected={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()}
for spec in list(old['roms'].values())+[old[k] for k in ('scene_cache','menu_assets','native_final_assets','title_bank_assets','hud_assets','sprite_assets')]:
    p=ROOT/'game-data'/spec['file'];protected[p.relative_to(ROOT).as_posix()]=digest(p)
helper=ROOT/'dist/PrepareCaptionAssets.exe';assert not helper.exists();shutil.copy2(ROOT/'build/pride-caption276-helper/tlk_prepare_caption_assets.exe',helper)
out=ROOT/'build/pride-caption283-publication';out.mkdir()
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-NonInteractive','-DataDirectory',str(ROOT/'game-data'),'-SnesRom',str(ROOT/'Lion King, The (USA).sfc'),'-MdRom',str(ROOT/'Lion King, The (World).md')]
with (out/'setup.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
new=json.loads(manifest.read_text());assert all(old[k]==new[k] for k in old if k!='prepared_utc')
assert all(digest(ROOT/p)==sha for p,sha in protected.items())
caption=ROOT/'game-data'/new['caption_assets']['file'];assert digest(caption)==b['caption_package_sha256']
launcher=ROOT/'scripts/RunInstalledPreview.ps1';assert launcher.read_text()==(archive/'scripts/RunInstalledPreview.ps1').read_text()
after=(base/'RunInstalledPreview.publish.ps1').read_text();assert 'dist/installed-preview277' in after and "'--caption-assets',$captions" in after
assert digest(package.parent/'LionKing.exe')==b['binary_sha256'];launcher.write_text(after)
checks=dict(default_setup_succeeded=True,all_previous_manifest_entries_preserved=all(old[k]==new[k] for k in old if k!='prepared_utc'),previous_assets_and_user_settings_preserved=all(digest(ROOT/p)==sha for p,sha in protected.items()),installed_caption_exact=digest(caption)==b['caption_package_sha256'],new_package_selected=launcher.read_text()==after)
paths=[Path(__file__),bp,package,proof,archive/'report.json',manifest,caption,helper,launcher,history,ROOT/'scripts/Setup.ps1']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,command=cmd,
    scope='Actual default Setup adds caption package only, preserves all existing manifest resources/asset bytes/settings; launcher selects prepared-caption277. One focused installed Windows run already inspected, no broad gameplay suites repeated. Other runtime extraction paths remain open.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'setup.log':digest(out/'setup.log')}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks,flush=True)
