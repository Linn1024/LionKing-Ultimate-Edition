"""Publish checkpoint prepared playback using the transactional caption workflow."""
from pathlib import Path
template293=Path(__file__).with_name('publish_pride_caption283.py')
source=template293.read_text().replace('pride-caption277-installed','pride-checkpoint287-installed').replace('installed-preview277','installed-preview287')
source=source.replace('pride-caption282-window','pride-checkpoint292-window').replace('pride-caption283-baseline','pride-checkpoint293-baseline').replace('pride-caption283-publication','pride-checkpoint293-publication')
source=source.replace('pride-caption275-baseline','pride-checkpoint285-baseline')
source=source.replace('dist/PrepareCaptionAssets.exe','dist/PrepareCheckpointAssets.exe').replace('pride-caption276-helper/tlk_prepare_caption_assets.exe','pride-checkpoint286-helper/tlk_prepare_checkpoint_assets.exe')
source=source.replace("new['caption_assets']","new['checkpoint_assets']").replace("b['caption_package_sha256']","b['checkpoint_package_sha256']")
source=source.replace("'--caption-assets',$captions","'--checkpoint-assets',$checkpoints")
source=source.replace("'hud_assets','sprite_assets')","'hud_assets','sprite_assets','caption_assets')")
source=source.replace('installed_caption_exact','installed_checkpoint_exact').replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template293,bp,')
source=source.replace('adds caption package only','adds checkpoint package only').replace('selects prepared-caption277','selects prepared-checkpoint287')
exec(compile(source,str(template293),'exec'))
