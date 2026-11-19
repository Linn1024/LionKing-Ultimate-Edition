"""Rebuild only the installed native HUD path and its two scene copy callers."""
from pathlib import Path
template307=Path(__file__).with_name('build_pride_revival297_installed.py')
source=template307.read_text().replace("ROOT/'build/pride-checkpoint287-installed'","ROOT/'build/pride-revival297-installed'")
source=source.replace("ROOT/'build/pride-revival297-installed';out.mkdir()","ROOT/'build/pride-native-hud307-installed';out.mkdir()")
source=source.replace('tlk_revival_art','tlk_native_hud').replace('revival-art.obj','native-hud.obj').replace('revival_reader','native_hud_reader')
source=source.replace("endswith('/libtlk_native_hud.a')","endswith('/runner/tlk_native_hud.c.obj')")
source=source.replace('pride-revival296-helper/tlk_prepare_revival_assets.exe','pride-native-hud306-helper/tlk_prepare_native_hud_assets.exe')
source=source.replace(",'--md-rom',str(ROOT/'Lion King, The (World).md')",'')
source=source.replace('revival.assets','native-hud.assets').replace('revival_package_sha256','native_hud_package_sha256')
source=source.replace('pride/wide/pride_repeat_render_wide.c','pride/wide/pride_repeat_prepared.c')
source=source.replace('prepare_revival_assets.c','prepare_native_hud_assets.c').replace('TlkRevivalAssets.cmake','TlkNativeHudAssets.cmake')
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template307,bp,')
source=source.replace('Installed revival images replace ROM decoding at first revival and saved-scene restoration via owned clones of validated startup data. --revival-assets required; explicit Setup error. Original image decoders installer-only; unrelated startup/font/metadata/hardware paths remain hybrid.',
    'Installed native health/roar meter glyphs replace ROM extraction at scene preparation and saved-scene staging via owned copies. --native-hud-assets required; explicit Setup error. Meter algorithms unchanged; other startup/metadata/hardware paths remain hybrid.')
exec(compile(source,str(template307),'exec'))
