"""Run the remaining launch candidate's real-window gates sequentially."""
import json
from pathlib import Path
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    saves=base/'launch-saves/report.json';assert bound(saves)['result']=='PASS'
    destination=base/'launch-lifecycle-batch-report.json';assert not destination.exists()
    stages=('pause','changed_source','previous_save','restart','regression','completion','route')
    commands={};results={};paths=[Path(__file__),saves]
    for stage in stages:
        script=ROOT/f'tools/verify_pride_lizard_launch_{stage}.py';paths.append(script)
        command=[sys.executable,str(script)];commands[stage]=command
        log_path=base/f'lifecycle-{stage}.log'
        assert not log_path.exists(),log_path
        print('Starting',stage,flush=True)
        with log_path.open('wb') as log:
            result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        results[stage]=result.returncode;paths.append(log_path)
        print('Finished',stage,'exit',result.returncode,flush=True)
        if result.returncode:break
    report=dict(result='PASS' if len(results)==len(stages) and not any(results.values()) else 'FAIL',
        commands=commands,stage_exit_codes=results,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        full_first_level_fidelity_complete=False)
    destination.write_text(json.dumps(report,indent=2)+'\n')
    assert report['result']=='PASS',results


if __name__=='__main__':main()
