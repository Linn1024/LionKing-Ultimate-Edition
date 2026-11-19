"""Fresh current-build gameplay checkpoint for the MD-timing source UI check."""
from pathlib import Path
template256=Path(__file__).with_name('verify_pride_menu233_gameplay_save.py')
source=template256.read_text().replace('pride-menu233-gameplay-save','pride-menu256-md-save')
anchor="(folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)"
assert anchor in source
source=source.replace(anchor,"(folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes()+(b'\\ngameplay.levels.pride_lands.final_life = md\\n' if flag=='--resource-profile' else b''));cmd[cmd.index(flag)+1]=str(folder/file)")
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template256,reference,')
source=source.replace('with only MD menu art and320 viewport selected','with MD final-life timing, MD menu art and320 viewport selected')
exec(compile(source,str(template256),'exec'))
