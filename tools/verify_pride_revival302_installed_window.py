"""One real installed checkpoint revival with the prepared image copy observed."""
from pathlib import Path
template302=Path(__file__).with_name('verify_pride_caption282_installed_window.py')
source=template302.read_text().replace('pride-caption282-window','pride-revival302-window')
source=source.replace('installed-preview277','installed-preview297').replace('pride-caption277-installed','pride-revival297-installed')
source=source.replace('pride-caption280-setup','pride-revival300-setup').replace('pride-caption276-helper/tlk_prepare_caption_assets.exe','pride-revival296-helper/tlk_prepare_revival_assets.exe')
source=source.replace("['caption_assets']","['revival_assets']").replace('captions.assets','revival.assets').replace('caption_assets=loaded','revival_assets=loaded')
source=source.replace("'caption.png'","'revival.png'").replace("'1500'","'5000'").replace("ROOT/'build/pride-caption270-clamp/idle.polled.tape'","ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape'")
source=source.replace("'schema = 1\\ngame = snes\\ndisplay.viewport = md\\n'","'schema = 1\\ngame = snes\\ndisplay.viewport = md\\ngameplay.levels.pride_lands.health_death = md\\n'")
source=source.replace("before['field']>=1030","before['field']>=4705").replace("1030<=before['field']<=after['field']<1150","4705<=before['field']<=after['field']<4770")
source=source.replace('time.monotonic()+70','time.monotonic()+110')
anchor="assert hwnd;capture_client(hwnd,out/'revival.png');after=reader.snapshot()";assert anchor in source
source=source.replace(anchor,"assert hwnd;before['prepared_revival_pointer']=reader.value('scene_revival_art');capture_client(hwnd,out/'revival.png');after=reader.snapshot()")
source=source.replace("checks=dict(actual_setup_package_matches_preparation=","checks=dict(prepared_image_copy_present=bool(before['prepared_revival_pointer']),actual_setup_package_matches_preparation=")
source=source.replace('paths=[Path(__file__),package,','paths=[Path(__file__),template302,package,')
source=source.replace('prepared_caption_load','prepared_revival_load').replace('actual_caption_interval','actual_revival_interval')
source=source.replace('one own-child Windows opening caption','one own-child Windows checkpoint revival with actual copied prepared artwork')
exec(compile(source,str(template302),'exec'))
