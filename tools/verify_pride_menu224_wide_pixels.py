"""32-bit: complete320 Continue clients against original-verified MD art."""
from pathlib import Path
script=Path(__file__).with_name('verify_pride_menu218_pixels.py')
source=script.read_text()
for before,after in [
    ("ROOT/'build/pride-menu217-windows/report.json'","ROOT/'build/pride-menu223-wide-windows/report.json'"),
    ("ROOT/'build/pride-menu218-pixels'","ROOT/'build/pride-menu224-wide-pixels'"),
    (',1,256,canvas)',',1,320,canvas)'),
    (',1,selected,256,canvas)',',1,selected,320,canvas)'),
    ('range(32,288)','range(0,320)'),
    ('picture==(512,448,image)','picture==(640,448,image)'),
    ('Complete actual256 Windows','Complete actual320 Windows'),
    ('No public/320/save/source-switch claim.','No public/save/source-switch claim.')]:
    assert before in source,before;source=source.replace(before,after)
source=source.replace('paths=[Path(__file__),capture,','paths=[Path(__file__),script,capture,')
exec(compile(source,str(script),'exec'))
