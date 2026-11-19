"""Repeat399 UI interaction with HWND refreshed after the first presentation."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride399_ui.py')
source=template.read_text().replace('build/pride399-ui','build/pride400-ui')
source=source.replace('    def key(vk):\n', '    def key(vk):\n        nonlocal_handle=window_for(proc.pid)\n        assert nonlocal_handle, ("Game window closed",proc.poll())\n')
source=source.replace('PostMessageW(hwnd,0x100','PostMessageW(nonlocal_handle,0x100').replace('PostMessageW(hwnd,0x101','PostMessageW(nonlocal_handle,0x101')
source=source.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(source,str(template),'exec'))
