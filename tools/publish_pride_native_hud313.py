"""Upgrade only native meter glyph data and select its prepared playback build."""
from pathlib import Path
template313=Path(__file__).with_name('publish_pride_caption283.py')
source=template313.read_text().replace('pride-caption277-installed','pride-native-hud307-installed').replace('installed-preview277','installed-preview307')
source=source.replace('pride-caption282-window','pride-native-hud312-window').replace('pride-caption283-baseline','pride-native-hud313-baseline').replace('pride-caption283-publication','pride-native-hud313-publication')
source=source.replace('pride-caption275-baseline','pride-native-hud305-baseline')
source=source.replace('dist/PrepareCaptionAssets.exe','dist/PrepareNativeHudAssets.exe').replace('pride-caption276-helper/tlk_prepare_caption_assets.exe','pride-native-hud306-helper/tlk_prepare_native_hud_assets.exe')
source=source.replace("new['caption_assets']","new['native_hud_assets']").replace("b['caption_package_sha256']","b['native_hud_package_sha256']")
source=source.replace("'--caption-assets',$captions","'--native-hud-assets',$nativeHud")
source=source.replace("'hud_assets','sprite_assets')","'hud_assets','sprite_assets','caption_assets','checkpoint_assets','revival_assets')")
source=source.replace('installed_caption_exact','installed_native_hud_exact').replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template313,bp,')
source=source.replace('adds caption package only','adds native meter glyph package only').replace('selects prepared-caption277','selects prepared-native-meter307')
exec(compile(source,str(template313),'exec'))
