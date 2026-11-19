"""Current226 resource-selected native Continue routes at native viewport width."""
from pathlib import Path
template253=Path(__file__).with_name('verify_pride_menu221_wide.py')
source=template253.read_text().replace('pride-menu221-wide','pride-menu253-native256')
source=source.replace('pride-menu215-native-art','pride-menu226-integrated')
anchor="if flag=='--resource-profile':text+='display.viewport = md\\n'"
assert anchor in source
source=source.replace(anchor,"if flag=='--resource-profile':text+='display.viewport = snes\\n'+('graphics.pride_final_menu = md\\n' if mode!='control' else '')")
source=source.replace("if mode!='control':env.update(TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))",'')
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template253,reference,')
source=source.replace('at320','at256').replace('private215 AOT/LLE','maintained226 resource-selected AOT/LLE')
exec(compile(source,str(template253),'exec'))
