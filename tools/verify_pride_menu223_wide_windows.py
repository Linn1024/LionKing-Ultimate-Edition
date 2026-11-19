"""Actual320 native-timing MD Continue views, against same-width controls."""
from pathlib import Path
script=Path(__file__).with_name('verify_pride_menu217_windows.py')
source=script.read_text()
for before,after in [
    ("ROOT/'build/pride-menu210-continue/report.json'","ROOT/'build/pride-menu221-wide/report.json'"),
    ("ROOT/'build/pride-menu217-windows'","ROOT/'build/pride-menu223-wide-windows'"),
    ("ref['commands'][case].copy()","ref['commands'][case+'-aot'].copy()"),
    ("reference.parent/case/'run.log'","reference.parent/(case+'-control')/'run.log'"),
    ('Actual native-timing MD-art Continue','Actual320 native-timing MD-art Continue'),
    ('No public/320/save/source-switch claim.','No public/save/source-switch claim.')]:
    assert before in source,before;source=source.replace(before,after)
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),script,reference,')
exec(compile(source,str(script),'exec'))
