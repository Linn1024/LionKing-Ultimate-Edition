"""Verify HUD publication and Ready through the real Windows Setup button."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_title_bank_setup_window.py')
source = original.read_text()
source = source.replace("build/pride-title-bank-installed/window", "build/pride-hud-assets/window")
anchor = "            checks['ready_message']"
assert source.count(anchor) == 1
source = source.replace(anchor, """            hud=data/manifest['hud_assets']['file']
            checks['hud_manifest']=manifest['hud_assets']['version']==1 and manifest['hud_assets']['source']=='megadrive'
            checks['hud_exact_payload']=digest(hud)==manifest['hud_assets']['sha256'] and hud.read_bytes()==(ROOT/'build/pride-hud-assets/hud.assets').read_bytes()
"""+anchor)
source = source.replace("paths=[Path(__file__),ROOT/'scripts/Setup.ps1']",
                        "paths=[Path(__file__),original,ROOT/'scripts/Setup.ps1',ROOT/'dist/PrepareHudAssets.exe']")
exec(compile(source, str(original), 'exec'))
