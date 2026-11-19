"""Publish current menu-tail correction only after terminal current regression gates."""
from pathlib import Path
verifier_source=Path(__file__).with_name('publish_pride_menu_output83.py')
source=verifier_source.read_text()
retired="    raise RuntimeError('Build83 is superseded by the verified Options effects-enable correction; do not publish it.')\n"
assert source.count(retired)==1;source=source.replace(retired,'')
source=source.replace("ROOT/'build/pride-menu-output83'","ROOT/'build/pride-menu-enable86'")
source=source.replace('installed-preview83','installed-preview86')
source=source.replace("('route','resume',","('route','enable',")
source=source.replace("'pride-menu-output83-owner-component'","'pride-menu-enable86-owner-component'")
source=source.replace("'pride-menu-output84-isolation'","'pride-menu-enable86-isolation'")
source=source.replace("build['unchanged_candidate80_inputs']==319","build['unchanged_candidate83_inputs']==321")
source=source.replace('pride-menu-publish83-baseline','pride-menu-publish86-baseline')
source=source.replace("folders.append('pride-menu-output83-baseline')","folders.append('pride-menu-enable86-baseline')")
anchor='    for path in proofs:';assert source.count(anchor)==1
source=source.replace(anchor,"    proofs += [ROOT/'build/pride-menu-enable85-md2/report.json',ROOT/'build/pride-menu-enable86-observer/report.json']\n"+anchor)
source=source.replace("('PASS','MENU_CUE_MEANINGS_VERIFIED')","('PASS','MENU_CUE_MEANINGS_VERIFIED','ORIGINAL_EFFECTS_ENABLE_CAPTURED','NEUTRAL_ENABLE_TRANSITION_OBSERVED')")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
