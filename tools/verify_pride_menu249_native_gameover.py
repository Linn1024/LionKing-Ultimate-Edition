"""Current maintained resource selection: native Game Over at both widths."""
from pathlib import Path

template249 = Path(__file__).with_name('verify_pride_menu222_game_over.py')
source = template249.read_text().replace('pride-menu222-game-over', 'pride-menu249-native-gameover')
source = source.replace('pride-menu215-native-art', 'pride-menu226-integrated')
anchor = "if flag=='--resource-profile' and width==320:text+='display.viewport = md\\n'"
assert anchor in source
source = source.replace(anchor, "if flag=='--resource-profile':text+=('display.viewport = md\\n' if width==320 else '')+('graphics.pride_final_menu = md\\n' if mode!='control' else '')")
source = source.replace("if mode!='control':env.update(TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))", '')
source = source.replace('paths=[Path(__file__),reference,', 'paths=[Path(__file__),template249,reference,')
source = source.replace('Private215 zero-credit', 'Maintained226 resource-selected zero-credit')
exec(compile(source, str(template249), 'exec'))
