"""Supplement the frozen difficulty audit with the appropriate wide route."""
import json
from pathlib import Path

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-restart-wide-bindings';out.mkdir();checks={}
    audit=ROOT/'build/pride-restart-difficulty-bindings/report.json'
    prior=bound(audit)
    checks['difficulty_audit_bound']=prior['result']=='PASS' and len(prior['checks'])==43 and all(prior['checks'].values())
    source=ROOT/'build/pride-restart-difficulty25/wide-completion/report.json'
    current=bound(source)
    checks['wide_route_11_passes']=current['result']=='PASS' and len(current['checks'])==11 and all(current['checks'].values())
    checks['ordinary_route']=current['ordinary_inputs'] and not current['guest_or_rom_edits']
    for label,cmd in current['commands'].items():
        checks[label+'_current_binary']=digest(Path(cmd[0]))==digest(ROOT/'build/pride-restart-difficulty25/player.exe')
        checks[label+'_no_state_or_practice']='--load' not in cmd and '--practice-level' not in cmd
    checks['fidelity_still_open']=current['full_first_level_fidelity_complete'] is False
    paths=[Path(__file__),audit,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
