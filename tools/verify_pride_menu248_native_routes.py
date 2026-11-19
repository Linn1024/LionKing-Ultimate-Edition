"""Current maintained source selection across native Continue routes at 320."""
from pathlib import Path

template248 = Path(__file__).with_name('verify_pride_menu221_wide.py')
source = template248.read_text().replace('pride-menu221-wide', 'pride-menu248-native-routes')
source = source.replace('pride-menu215-native-art', 'pride-menu226-integrated')
source = source.replace("if flag=='--resource-profile':text+='display.viewport = md\\n'", "if flag=='--resource-profile':text+='display.viewport = md\\n'+('graphics.pride_final_menu = md\\n' if mode!='control' else '')")
source = source.replace("if mode!='control':env.update(TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))", '')
source = source.replace('paths=[Path(__file__),reference,', 'paths=[Path(__file__),template248,reference,')
source = source.replace('private215 AOT/LLE', 'maintained226 resource-selected AOT/LLE')
exec(compile(source, str(template248), 'exec'))
