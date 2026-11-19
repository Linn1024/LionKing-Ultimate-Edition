"""Current cold-load F12 source switching, with lossless small diagnostic output."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
seed_report=ROOT/'build/pride-menu233-gameplay-save/report.json';assert bound(seed_report)['result']=='PASS'
script=Path(__file__).with_name('verify_pride_menu229_resource_ui.py')
source=script.read_text().replace("ROOT/'build/pride-menu229-resource-ui'","ROOT/'build/pride-menu234-resource-ui'")
anchor="cmd+=['--menu-at','4400','--menu-page','resources']";assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\ncmd+=['--load',str(seed_report.parent/'current.state')]")
anchor="trace=out/'tree.jsonl';env=";assert source.count(anchor)==1
source=source.replace(anchor,"trace=out/'tree.jsonl.gz';trace_capture=JsonPipe(trace);env=")
source=source.replace("env['TLK_SOFT_TREE_LOG']=str(trace)","env['TLK_SOFT_TREE_LOG']=trace_capture.name").replace('latest(trace)','trace_capture.latest()')
anchor="checks['clean_exit']=proc.returncode==0";assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\ntrace_metadata=trace_capture.finish()\n(out/'trace-metadata.json').write_text(json.dumps(trace_metadata,indent=2)+'\\n')")
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),script,seed_report,Path(__file__).with_name(\'windows_json_pipe.py\'),reference,')
try:exec(compile(source,str(script),'exec'))
except BaseException as error:
    if 'trace_capture' in globals():
        metadata=trace_capture.finish();(out/'trace-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (out/'attempt-report.json').write_text(json.dumps(dict(result='FAIL',error=repr(error),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),script,seed_report]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
    raise
