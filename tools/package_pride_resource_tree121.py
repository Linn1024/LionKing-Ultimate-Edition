"""Stage118 tree repair with retained verified probe module; public remains86."""
from pathlib import Path
verifier_source=Path(__file__).with_name('package_pride_hyena_probe107.py')
source=verifier_source.read_text().replace("base=ROOT/'build/pride-hyena-probe103'","base=ROOT/'build/pride-resource-tree118'").replace("ROOT/'dist/installed-preview103'","ROOT/'dist/installed-preview118'")
old="proofs=[base/'routes-qualification106/report.json',base/'fights104/report.json',base/'windows-ui-qualification104/report.json',ROOT/'build/pride-hyena-probe103-original/report.json',ROOT/'build/pride-hyena-probe103-component/report.json']"
new="proofs=[base/'routes99/report.json',base/'parent-verification/report.json',base/'windows-ui119/report.json',ROOT/'build/pride-hyena-probe103-original/report.json',ROOT/'build/pride-hyena-probe103-component/report.json',ROOT/'build/pride-hyena-probe103/fights104/report.json']"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace("info['hyena_walking_probe_scope']=","info['resource_group_scope']='Stable resource group IDs; inherited Continue-token artwork/palette follow their graphics group independently of Options audio'\ninfo['hyena_walking_probe_scope']=")
source=source.replace('development preview103','development preview118').replace('dist/installed-preview103','dist/installed-preview118')
source=source.replace('Compiled game code and remaining','Group choices apply to inherited children; individual choices override them.\\n\\nCompiled game code and remaining')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
