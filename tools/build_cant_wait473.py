"""Build independent rhino tail colors; shared original tail artwork is unchanged."""
from pathlib import Path
template=Path(__file__).with_name('build_pride398.py')
s=template.read_text().replace("base=ROOT/'build/pride390'","base=ROOT/'build/cant-wait460'").replace("out=ROOT/'build/pride398'","out=ROOT/'build/cant-wait473'")
a=s.index('rows=json.loads(');b=s.index('for label,template,src in tasks:',a)
s=s[:a]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('wide',b['compiles']['wide'],None)]\n"+s[b:]
s=s.replace("'engine/runner/tlk_menu_imgui.cpp',","'engine/runner/tlk_wide.c','engine/runner/tlk_cw_tail_metadata.h','engine/runner/tlk_cw_rhino_metadata.h',")
s=s.replace('Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.','Independent second-level rhino tail palette using shared original images and existing prepared scene palette. Only resources/compositor objects change; no behavior, audio, assets or save-schema changes.')
exec(compile(s,str(template),'exec'))
