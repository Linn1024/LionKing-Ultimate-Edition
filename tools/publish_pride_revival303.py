"""Publish prepared revival artwork using the existing transactional upgrade path."""
from pathlib import Path
template303=Path(__file__).with_name('publish_pride_caption283.py')
source=template303.read_text().replace('pride-caption277-installed','pride-revival297-installed').replace('installed-preview277','installed-preview297')
source=source.replace('pride-caption282-window','pride-revival302-window').replace('pride-caption283-baseline','pride-revival303-baseline').replace('pride-caption283-publication','pride-revival303-publication')
source=source.replace('pride-caption275-baseline','pride-revival295-baseline')
source=source.replace('dist/PrepareCaptionAssets.exe','dist/PrepareRevivalAssets.exe').replace('pride-caption276-helper/tlk_prepare_caption_assets.exe','pride-revival296-helper/tlk_prepare_revival_assets.exe')
source=source.replace("new['caption_assets']","new['revival_assets']").replace("b['caption_package_sha256']","b['revival_package_sha256']")
source=source.replace("'--caption-assets',$captions","'--revival-assets',$revival")
source=source.replace("'hud_assets','sprite_assets')","'hud_assets','sprite_assets','caption_assets','checkpoint_assets')")
source=source.replace('installed_caption_exact','installed_revival_exact').replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template303,bp,')
source=source.replace('adds caption package only','adds revival package only').replace('selects prepared-caption277','selects prepared-revival297')
exec(compile(source,str(template303),'exec'))
