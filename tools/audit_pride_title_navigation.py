"""Bind independent title navigation, source UI, legacy records and retained failures."""
import json
from pathlib import Path
import re
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-title-navigation-bindings';out.mkdir();checks={};reports={}
    names=['pride-title-navigation-edges/report.json','pride-title-navigation-edges2/report.json',
           'pride-title-navigation-model/report.json','pride-title-navigation-model2/report.json',
           'pride-title-navigation-state/report.json','pride-title-navigation-hooks/generation-report.json',
           'pride-title-ready-hooks/generation-report.json',
           'pride-title-navigation19/build-report.json','pride-title-navigation20/build-report.json',
           'pride-title-navigation20/verification/report.json','pride-title-navigation21/build-report.json',
           'pride-title-navigation21/verification/report.json','pride-title-navigation21/switch/report.json',
           'pride-title-navigation22/build-report.json','pride-title-navigation22/switch/report.json',
           'pride-title-navigation22/switch2/report.json','pride-title-navigation23/build-report.json',
           'pride-title-navigation23/verification/report.json','pride-title-navigation23/boot/report.json',
           'pride-title-navigation23/switch2/report.json','pride-title-navigation23/continue-regressions/report.json',
           'pride-title-navigation23/mixtures/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for index,count in [(1,18),(3,22),(4,60),(11,424),(17,240),(18,14),(19,15),(20,171),(21,50)]:
        r=reports[names[index]];checks[names[index]+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    failed=reports[names[9]]
    checks['retained_opposing_direction_failure']=failed['result']=='FAIL' and [k for k,v in failed['checks'].items() if not v]==['256_both-directions_original_visible_outcome','320_both-directions_original_visible_outcome']
    checks['retained_source_restart_failure']=reports[names[12]]['result']=='FAIL' and reports[names[12]]['checks']['md-from-gameplay_restarted'] is False
    checks['retained_early_restart_endpoint_failure']=reports[names[14]]['result']=='FAIL'
    checks['retained_old_logger_stage_checks']=reports[names[15]]['result']=='FAIL'
    checks['retained_unpatched_catalog_stop']=b'Development MD menu art requires' in (ROOT/'build/pride-title-navigation19/verification/256-control-idle/run.log').read_bytes()
    gen=ROOT/'build/pride-title-navigation-hooks';generation=reports[names[5]]
    checks['generated_hashes']=all(digest(gen/p)==sha for p,sha in generation['generated_sha256'].items())
    checks['same_configured_program_contract']=generation['program_contract_sha256']==reports[names[6]]['program_contract_sha256']
    checks['sixteen_generated_units']=len(generation['instrumented_units'])==16
    text=(gen/'hooks/bankc4_part1c_v2.c').read_text()
    checks['generated_menu_hook']='PrideSceneCompiledPreOpcode(cpu,0xC4677Bu)' in text
    base=ROOT/'build/pride-title-navigation23';build=reports[names[16]]
    checks['current_binary']=digest(base/'player.exe')==build['binary_sha256']
    checks['all_317_link_inputs']=len(build['link_inputs_sha256'])==317 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    prior=ROOT/'build/pride-title-navigation21'
    for name in ('navigation.obj','state.obj','bankc4_part1c_v2.c.obj'):
        checks[name+'_unchanged_from_qualified21']=digest(base/name)==digest(prior/name)
    catalog=(base/'game/tlk_resources.c').read_text()
    rows=re.findall(r'^\s*\{"([^"]+)", "[^"]*", (-?\d+),',catalog,re.M)
    node=next(i for i,r in enumerate(rows) if r[0]=='gameplay.menus.title_navigation')
    checks['catalog_menu_parent']=rows[int(rows[node][1])][0]=='gameplay.menus' and int(rows[node][1])<node
    checks['required_game_overlays']='gameplay.levels.pride_lands.health_death' in catalog and 'gameplay.levels.pride_lands.random_entry' in catalog
    frontend=(base/'frontend/sdl_main.c').read_text()
    checks['source_aware_restart_macro']='if(TlkResourcesUseMd("gameplay.menus.title_navigation"))MacroWait(6);' in frontend and 'else MacroTap(UP);' in frontend
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/n for n in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
