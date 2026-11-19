"""Bind the input-only difficulty repair and its retained failures."""
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-restart-difficulty-bindings';out.mkdir()
    checks={};reports={}
    names=['pride-title-navigation23/build-report.json',
           'pride-restart-difficulty24/build-report.json',
           'pride-restart-difficulty25/build-report.json',
           'pride-restart-prefix-observer26/build-report.json',
           'pride-restart-difficulty-fixtures/report.json',
           'pride-restart-difficulty24/difficulty/report.json',
           'pride-restart-difficulty25/difficulty/report.json',
           'pride-restart-difficulty25/replay/report.json',
           'pride-restart-difficulty25/completion/report.json',
           'pride-restart-prefix-observer26/capture/report.json',
           'pride-restart-prefix-adapt0/report.json',
           'pride-restart-prefix-spaced0/report.json',
           'pride-restart-prefix-spaced99/report.json',
           'pride-restart-difficulty25/completion2/report.json',
           'pride-restart-difficulty25/difficulty-lle/report.json']
    for name in names:
        reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for index,count in [(4,38),(6,78),(7,94),(9,10),(14,13)]:
        r=reports[names[index]]
        checks[names[index]+'_passes']=r['result'] in ('PASS','NEUTRAL') and len(r['checks'])==count and all(r['checks'].values())
    for index,passed,total in [(5,9,13),(8,20,24)]:
        r=reports[names[index]]
        checks[names[index]+'_retained_failure']=r['result']=='FAIL' and sum(r['checks'].values())==passed and len(r['checks'])==total
    checks['retained_early_options_probe']=reports[names[10]]['result']=='FAIL'
    route=reports[names[13]]
    checks['wide_route_failure_explicit']=route['result']=='FAIL' and len(route['checks'])==32 and sum(route['checks'].values())==30 and [k for k,v in route['checks'].items() if not v]==['320-md_next_level','320-md-lle_next_level']
    current=reports[names[2]];previous=reports[names[0]]
    for index in range(4):
        r=reports[names[index]];folder=(ROOT/'build'/names[index]).parent
        checks[folder.name+'_binary']=digest(folder/'player.exe')==r['binary_sha256']
        checks[folder.name+'_317_inputs']=len(r['link_inputs_sha256'])==317 and all(digest(ROOT/p)==sha for p,sha in r['link_inputs_sha256'].items())
    old_inputs=previous['link_inputs_sha256'];new_inputs=current['link_inputs_sha256']
    removed=set(old_inputs)-set(new_inputs);added=set(new_inputs)-set(old_inputs)
    checks['only_host_replaced']=len(removed)==len(added)==1 and all(Path(p).name=='host.obj' for p in removed|added)
    checks['shared_inputs_unchanged']=all(old_inputs[p]==new_inputs[p] for p in set(old_inputs)&set(new_inputs))
    frontend=(ROOT/'build/pride-restart-difficulty25/frontend/sdl_main.c').read_text()
    checks['correct_difficulty_address']='unsigned difficulty=Wram16(0x1ff92);' in frontend
    checks['ordinary_input_compensation']='for(unsigned i=0;i<difficulty;i++) { MacroTap(A); MacroWait(20); }' in frontend
    checks['capture_before_boot']=frontend.index('unsigned difficulty=Wram16(0x1ff92);')<frontend.index('BuildLevelMacro(level, s_sel_invul, difficulty);')
    corrected=reports[names[12]];cmd=corrected['command']
    derived=Path(cmd[cmd.index('--input-polled')+1]).read_bytes()
    original=(ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape').read_bytes()
    checks['credited_gameplay_suffix_exact']=derived[(638+99)*2:]==original[638*2:]
    checks['no_guest_edit_or_practice']=corrected['ordinary_inputs'] and not corrected['guest_or_rom_edits'] and '--load' not in cmd and '--practice-level' not in cmd
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/name for name in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
