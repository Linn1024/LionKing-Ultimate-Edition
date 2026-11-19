"""Live HUD edit: dismiss the ordinary Applied dialog before resuming."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride420_hud_ui.py')
s=template.read_text().replace('build/pride420-hud-ui','build/pride422-hud-ui').replace("r['field']==1500","r['field']==2200").replace("r['field']>=1650","r['field']>=2350")
s=s.replace("capture_client(hwnd,out/'hud-options.png');key(0x71)","capture_client(hwnd,out/'hud-options.png');key(0x71);applied=wait(lambda r:choices(r)[children[1]][4]==1);snapshots['applied']=applied;checks['no_restart']=applied['field']==initial['field'];key(0x1b);key(0x1b);key(0x1b)")
s=s.replace("exec(compile(s,str(template),'exec'))", "s=s.replace(\"'--menu-at','1500'\",\"'--menu-at','2200'\")\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))
