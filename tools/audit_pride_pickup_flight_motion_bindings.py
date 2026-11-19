"""Bind the flight component without claiming an enabled runtime adapter."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-pickup-flight-motion-bindings';out.mkdir();checks={}
    path=ROOT/'build/pride-pickup-flight-motion2/report.json';r=bound(path)
    checks['original_cpu_component_2311_passes']=r['result']=='PASS' and len(r['checks'])==2311 and all(r['checks'].values())
    checks['2240_original_action_fixtures']=len(r['fixtures'])==2240 and {x['version'] for x in r['fixtures']}=={'md','snes'}
    checks['both_natural_flights']=len(r['natural'])==2 and sum(x['samples'] for x in r['natural'])==70
    checks['shared_motion_streams']=r['checks']['motion_tokens_match']
    checks['intercepts_explicit']=len(r['native_intercepts'])==len(r['md_intercepts'])==4 and r['animation_displacement_intercepted']
    checks['no_rom_instruction_edits']=r['original_rom_instructions_modified'] is False
    checks['runtime_not_enabled']=r['production_adapter_enabled'] is False
    current=ROOT/'build/pride-audio-prime30/build-report.json';build=bound(current)
    checks['current_player_unchanged']=digest(current.parent/'player.exe')==build['binary_sha256']
    checks['current_317_inputs_unchanged']=len(build['link_inputs_sha256'])==317 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),path,current]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
