"""Build independent roar/health/lives artwork using the current frontend."""
from pathlib import Path
template=Path(__file__).with_name('build_pride398.py')
s=template.read_text().replace("base=ROOT/'build/pride390'","base=ROOT/'build/pride398'").replace("out=ROOT/'build/pride398'","out=ROOT/'build/pride418'")
start=s.index('rows=json.loads(');end=s.index('for label,template,src in tasks:',start)
s=s[:start]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('wide',b['compiles']['wide'],None)]\n"+s[end:]
s=s.replace("'engine/runner/tlk_menu_imgui.cpp',","'engine/runner/tlk_wide.c',")
s=s.replace('Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.','Independent Pride HUD roar, health and lives artwork with inherited whole-HUD selection. Only resources and compositor objects changed; no guest, audio, assets or save changes.')
exec(compile(s,str(template),'exec'))
