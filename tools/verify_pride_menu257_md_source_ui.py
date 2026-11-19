"""Real F12 source edits from MD-timing Continue and visible restarted gameplay."""
from pathlib import Path

template257=Path(__file__).with_name('verify_pride_menu234_resource_ui.py')
def tailor257(source):
    anchor="(out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)"
    assert anchor in source
    source=source.replace(anchor,"(out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes()+(b'\\ngameplay.levels.pride_lands.final_life = md\\n' if flag=='--resource-profile' else b''));cmd[cmd.index(flag)+1]=str(out/file)")
    anchor="checks['paused_owned_native_menu']=owned['active']==1 and owned['art_mode']==1 and owned['transition_mode']==0"
    assert anchor in source
    source=source.replace(anchor,"checks['paused_owned_md_timing_menu']=owned['active']==0 and owned['art_mode']==1 and owned['transition_mode']==1 and reader.value('final_scene_entry')>0 and owned['health']==0")
    anchor="            state=reader.snapshot();snapshots[label+'-after']=after;"
    assert anchor in source
    source=source.replace(anchor,"            snapshots[label+'-initial-transition']=after\n            settle_at=after['field']+256\n            after=wait(lambda r:r['field']>=settle_at and r['descriptor']==0xc00387 and r['health']>0 and r['macro_index']==r['macro_length'])\n"+anchor)
    anchor="checks[label+'_native_owner_cleared_and_mode_refreshed']=state['active']==0 and state['credits_art']==0 and state['art_mode']==(value==2)"
    assert anchor in source
    source=source.replace(anchor,"checks[label+'_owners_cleared_and_mode_refreshed']=state['active']==0 and state['credits_art']==0 and state['art_mode']==(value==2) and reader.value('final_scene_entry')==0 and reader.value('final_menu_confirmed_credits')==0")
    source=source.replace('paths=[Path(__file__),script,seed_report,','paths=[Path(__file__),template257,script,seed_report,')
    source=source.replace('from native Continue','from MD-timing Continue')
    return source
source=template257.read_text().replace('pride-menu234-resource-ui','pride-menu257-md-source-ui').replace('pride-menu233-gameplay-save','pride-menu256-md-save')
anchor="try:exec(compile(source,str(script),'exec'))";assert source.count(anchor)==1
source=source.replace(anchor,'source=tailor257(source)\n'+anchor)
exec(compile(source,str(template257),'exec'))
