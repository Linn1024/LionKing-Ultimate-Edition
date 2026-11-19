"""Build the existing shared HUD for the owned third-level scene."""
from pathlib import Path
template=Path(__file__).with_name('build_pride398.py')
s=template.read_text().replace("base=ROOT/'build/pride390'","base=ROOT/'build/cant-wait482'").replace("out=ROOT/'build/pride398'","out=ROOT/'build/graveyard493'")
a=s.index('rows=json.loads(');b=s.index('for label,template,src in tasks:',a)
s=s[:a]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('wide',b['compiles']['wide'],None)]\n"+s[b:]
s=s.replace("'engine/runner/tlk_menu_imgui.cpp',","'engine/runner/tlk_wide.c',")
s=s.replace('Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.','Shared prepared cub HUD renderer enabled in owned Elephant Graveyard scene; independent component choices retained. Resources/compositor only; gameplay, audio, assets and save schema unchanged.')
exec(compile(s,str(template),'exec'))
