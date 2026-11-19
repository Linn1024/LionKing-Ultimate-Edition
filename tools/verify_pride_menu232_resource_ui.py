"""Correct229's interactive power-on launch; retain JSONL losslessly compressed."""
from pathlib import Path
from windows_json_pipe import JsonPipe
script=Path(__file__).with_name('verify_pride_menu229_resource_ui.py')
source=script.read_text().replace("ROOT/'build/pride-menu229-resource-ui'","ROOT/'build/pride-menu232-resource-ui'")
anchor="cmd+=['--menu-at','4400','--menu-page','resources']"
assert source.count(anchor)==1
source=source.replace(anchor,"i=cmd.index('--frames');del cmd[i:i+2]\n"+anchor)
anchor="trace=out/'tree.jsonl';env=";assert source.count(anchor)==1
source=source.replace(anchor,"trace=out/'tree.jsonl.gz';trace_capture=JsonPipe(trace);env=")
source=source.replace("env['TLK_SOFT_TREE_LOG']=str(trace)","env['TLK_SOFT_TREE_LOG']=trace_capture.name")
source=source.replace('latest(trace)','trace_capture.latest()')
anchor="checks['clean_exit']=proc.returncode==0";assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\ntrace_metadata=trace_capture.finish()\n(out/'trace-metadata.json').write_text(json.dumps(trace_metadata,indent=2)+'\\n')")
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),script,Path(__file__).with_name(\'windows_json_pipe.py\'),reference,')
exec(compile(source,str(script),'exec'))
