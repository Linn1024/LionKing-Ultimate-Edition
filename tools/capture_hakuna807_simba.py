"""Accept actual Simba captures only after visible gameplay pixels are present."""
from pathlib import Path
from PIL import Image
template=Path(__file__).with_name('capture_hakuna797_simba.py')
s=template.read_text().replace('build/hakuna797-simba','build/hakuna807-simba').replace('threshold=1600','threshold=2250')
s=s.replace("capture_client(hwnd,folder/'actual.png');captured=row", "capture_client(hwnd,folder/'actual.png');captured=row if len(Image.open(folder/'actual.png').convert('RGB').getcolors(65536) or [0]*65537)>16 else None")
exec(compile(s,str(template),'exec'))
