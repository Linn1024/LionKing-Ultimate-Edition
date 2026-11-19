"""Keep posted motion and click together in the Windows event queue."""
from pathlib import Path

original_mouse_verifier=Path(__file__).with_name('verify_pride_soft_tree_mouse.py')
source=original_mouse_verifier.read_text()
source=source.replace("out=base/'windows-mouse'/args.case","out=base/'windows-mouse-queue'/args.case")
source=source.replace('0x200,0,x+(y<<16));time.sleep(.1)', '0x200,0,x+(y<<16));')
source=source.replace('paths=[Path(__file__),original_verifier,','paths=[Path(__file__),original_mouse_verifier,original_verifier,')
exec(compile(source,str(original_mouse_verifier),'exec'))
