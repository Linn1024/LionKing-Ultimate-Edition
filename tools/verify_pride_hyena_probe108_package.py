"""Installed103 uses default prepared data and preserves the qualified MD route."""
from pathlib import Path
wrapper=Path(__file__).with_name('verify_pride_menu_output83_package.py')
script=wrapper.read_text().replace('pride-menu-output83','pride-hyena-probe103').replace('installed-preview83','installed-preview103')
anchor="exec(compile(source,str(verifier_source),'exec'))";assert script.count(anchor)==1
adjust='''
source=source.replace("base/'route/report.json'","base/'routes-qualification106/report.json'")
source=source.replace("original=source.parent/'menus-aot'","original=base/'routes99/probe-aot'")
source=source.replace("tape=Path(prior['commands']['menus-aot'][prior['commands']['menus-aot'].index('--input-polled')+1])","route=bound(base/'routes99/report.json');command=route['commands']['probe-aot'];tape=Path(command[command.index('--input-polled')+1])")
source=source.replace('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/"tools/verify_pride_menu_output83_package.py",')
'''
script=script.replace(anchor,adjust+'\n'+anchor)
exec(compile(script,str(wrapper),'exec'))
