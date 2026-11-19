"""Current118 package and prepared default data against its selected full route."""
from pathlib import Path
wrapper=Path(__file__).with_name('verify_pride_menu_output83_package.py')
script=wrapper.read_text().replace('pride-menu-output83','pride-resource-tree118').replace('installed-preview83','installed-preview118')
anchor="exec(compile(source,str(verifier_source),'exec'))";assert script.count(anchor)==1
adjust='''
source=source.replace("base/'route/report.json'","base/'routes99/report.json'")
source=source.replace("source.parent/'menus-aot'","source.parent/'probe-aot'")
source=source.replace("prior['commands']['menus-aot']","prior['commands']['probe-aot']")
source=source.replace('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/"tools/verify_pride_menu_output83_package.py",')
'''
script=script.replace(anchor,adjust+'\n'+anchor)
exec(compile(script,str(wrapper),'exec'))
