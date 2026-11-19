"""Reuse installed-caption build orchestration for the checkpoint-only migration."""
from pathlib import Path
template287=Path(__file__).with_name('build_pride_caption277_installed.py')
source=template287.read_text().replace("ROOT/'build/pride-caption268'","ROOT/'build/pride-caption277-installed'")
source=source.replace("ROOT/'build/pride-caption277-installed';out.mkdir()","ROOT/'build/pride-checkpoint287-installed';out.mkdir()")
source=source.replace('pride-caption276-helper/tlk_prepare_caption_assets.exe','pride-checkpoint286-helper/tlk_prepare_checkpoint_assets.exe')
source=source.replace('tlk_title_art','tlk_checkpoint_art').replace('title-art.obj','checkpoint-art.obj').replace('caption_reader','checkpoint_reader')
source=source.replace('captions.assets','checkpoints.assets').replace('caption_package_sha256','checkpoint_package_sha256')
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template287,bp,')
source=source.replace('Installed caption reader replaces startup title-art ROM extraction. Requires --caption-assets; explicit Setup error, no decoder fallback. Original extraction compiled into installer only. Other startup components remain hybrid/migration work.',
    'Installed checkpoint reader replaces startup checkpoint ROM extraction. Requires --checkpoint-assets; explicit Setup error, no decoder fallback. Original extraction compiled into installer only. Caption migration retained; other startup components remain hybrid/migration work.')
exec(compile(source,str(template287),'exec'))
