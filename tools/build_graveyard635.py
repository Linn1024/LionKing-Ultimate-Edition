"""Rebuild only the resource tree and audio coordinator for Graveyard death/retry."""
from pathlib import Path
template=Path(__file__).with_name('build_pride398.py')
s=template.read_text().replace("base=ROOT/'build/pride390'", "base=ROOT/'build/graveyard621'").replace("out=ROOT/'build/pride398'", "out=ROOT/'build/graveyard635'")
a=s.index('rows=json.loads(');b=s.index('for label,template,src in tasks:',a)
s=s[:a]+"tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('audio',b['compiles']['audio'],out/'game/tlk_audio.c')]\n"+s[b:]
s=s.replace("'engine/runner/tlk_menu_imgui.cpp',", "'engine/runner/tlk_audio.c',")
s=s.replace('Available MD draft preset, preserved branch inheritance and explicit SNES for unavailable leaves. SDL MD footer/F7 and ImGui button. No guest, audio, artwork, installed-data or save-schema changes.',__doc__)
exec(compile(s,str(template),'exec'))
