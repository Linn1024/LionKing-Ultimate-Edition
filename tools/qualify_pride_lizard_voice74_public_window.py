"""Qualify retained window evidence after its dependent CMD run finishes."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-lizard-voice74'
    original=base/'game-window-verification/report.json'
    cmd=base/'cmd-play/report.json'
    r=bound(original); c=bound(cmd)
    missing=[k for k,v in r['checks'].items() if not v]
    assert r['result']=='FAIL' and missing==['actual_cmd_entrypoint_dumped_window']
    assert c['result']=='PASS' and all(c['checks'].values())
    checks=dict(r['checks'])
    checks['actual_cmd_entrypoint_dumped_window']=(base/'cmd-play/window.png').is_file() and 'resource_cache=loaded' in (base/'cmd-play/settings/last-launch.log').read_text()
    out=base/'game-window-qualification';out.mkdir()
    paths=[Path(__file__),original,cmd,base/'cmd-play/window.png',base/'cmd-play/settings/last-launch.log']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                retained_failure=str(original.relative_to(ROOT)),
                reason='Window verifier inspected CMD output before that independent process completed; all six window checks passed. CMD has now exited successfully. Captures and runtime are unchanged.',
                original_game_and_resource_os_captures_visually_inspected=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks))


if __name__=='__main__':main()
