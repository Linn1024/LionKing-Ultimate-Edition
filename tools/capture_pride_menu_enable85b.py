"""Correct byte access for the word-swapped original MD effects flag."""
from pathlib import Path
verifier_source=Path(__file__).with_name('capture_pride_menu_enable85.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-enable85-md'","ROOT/'build/pride-menu-enable85-md2'")
source=source.replace('game.work_ram[0xf284]','game.work_ram[0xf285]').replace('game.work_ram[0xf283]','game.work_ram[0xf282]')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
