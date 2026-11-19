"""Current entrance-window package/default imported data and full selected route."""
from pathlib import Path
wrapper=Path(__file__).with_name('verify_pride_menu_output83_package.py')
script=wrapper.read_text().replace('pride-menu-output83','pride-hyena-entrance139').replace('installed-preview83','installed-preview139')
anchor="exec(compile(source,str(verifier_source),'exec'))";assert script.count(anchor)==1
adjust='''
source=source.replace("base/'route/report.json'","base/'routes156-qualification/report.json'")
source=source.replace("source.parent/'menus-aot'","base/'routes148/probe-aot'")
source=source.replace("prior['commands']['menus-aot']","prior['commands']['probe-aot']")
source=source.replace('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/"tools/verify_pride_menu_output83_package.py",')
'''
script=script.replace(anchor,adjust+'\n'+anchor)
exec(compile(script,str(wrapper),'exec'))
