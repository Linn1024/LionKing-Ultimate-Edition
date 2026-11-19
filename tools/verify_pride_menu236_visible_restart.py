"""Follow234's state checks through the native revival transition to visible world."""
from pathlib import Path
launcher236=Path(__file__).with_name('verify_pride_menu234_resource_ui.py')
def settle236(s):
    anchor="            state=reader.snapshot();snapshots[label+'-after']=after;"
    assert s.count(anchor)==1
    s=s.replace(anchor,"            snapshots[label+'-initial-transition']=after\n            settle_at=after['field']+256\n            after=wait(lambda r:r['field']>=settle_at and r['descriptor']==0xc00387 and r['health']>0 and r['macro_index']==r['macro_length'])\n"+anchor)
    s=s.replace('paths=[Path(__file__),script,seed_report,','paths=[Path(__file__),launcher236,script,seed_report,')
    return s
source=launcher236.read_text().replace('pride-menu234-resource-ui','pride-menu236-visible-restart')
anchor="try:exec(compile(source,str(script),'exec'))";assert source.count(anchor)==1
source=source.replace(anchor,"source=settle236(source)\n"+anchor)
exec(compile(source,str(launcher236),'exec'))
