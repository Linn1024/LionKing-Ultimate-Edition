"""Bind the published player to its newly prepared rhino sprite policy."""
from pathlib import Path
from audit_scenes import ROOT
import shutil
template=Path(__file__).with_name('publish_cant_wait466.py')
old=ROOT/'dist/installed-preview460/package.json';failed=ROOT/'build/cant-wait466-publication/attempt-package.json'
if old.exists() and not failed.exists():shutil.copy2(old,failed)
s=template.read_text().replace('build/cant-wait466-publication','build/cant-wait467-publication')
s=s.replace("exec(compile(s,str(template),'exec'))", "s=s.replace(\"info['required_sprite_assets_version']=2\",\"info['required_sprite_assets_version']=2;info['required_sprite_policy_sha256']=(helper.parent/'sprites.assets').read_bytes()[88:120].hex()\")\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))
