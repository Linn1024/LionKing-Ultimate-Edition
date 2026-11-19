"""Build independently selected ostrich colors on the current second-level player."""
from pathlib import Path
template=Path(__file__).with_name('build_pride398.py')
s=template.read_text().replace("base=ROOT/'build/pride390'","base=ROOT/'build/cant-wait440'").replace("out=ROOT/'build/pride398'","out=ROOT/'build/cant-wait448'")
a=s.index('rows=json.loads(');b=s.index('for label,template,src in tasks:',a)
s=s[:a]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('wide',b['compiles']['wide'],None)]\n"+s[b:]
s=s.replace("'engine/runner/tlk_menu_imgui.cpp',","'engine/runner/tlk_wide.c','engine/runner/tlk_cw_monkey_metadata.h','engine/runner/tlk_cw_ostrich_metadata.h',")
s=s.replace('Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.','Independent original MD monkey and ostrich colors in second-level owned draws. Only resources/compositor objects change; prepared palette controller, native artwork, guest, audio and saves retained.')
exec(compile(s,str(template),'exec'))
