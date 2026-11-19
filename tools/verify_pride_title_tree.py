"""Exercise all four independent caption choices in the real resource menu."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_popup_tree.py')
source=original.read_text()
changes={
    "BRANCH='graphics.sprites.effects.pickup_arrival'":"BRANCH='graphics.titles.pride_lands'",
    "ROOT/'build/pride-popup-work'":"ROOT/'build/pride-title-work'",
    "base/'commands4.json'":"base/'final-build3.json'",
    "'--frames',1672":"'--frames',1008",
    "'--menu-at',1664":"'--menu-at',1000",
    "r['field']==1664":"r['field']==1000",
    "setchoice(BRANCH+'.position',1)":"setchoice(BRANCH+'.position',1);setchoice(BRANCH+'.duration',1)",
    "setchoice(BRANCH+'.position',2)":"setchoice(BRANCH+'.position',2);setchoice(BRANCH+'.duration',2)",
    "('frames','palette','position')":"('frames','palette','position','duration')",
    '==[2,1,1]':'==[2,1,1,1]',
    '==[1,2,2]':'==[1,2,2,2]',
    '==[1,1,1]':'==[1,1,1,1]',
    'paths=[Path(__file__),report_path,':'paths=[Path(__file__),original,report_path,',
}
for before,after in changes.items():
    assert before in source,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
