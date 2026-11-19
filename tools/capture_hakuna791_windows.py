"""Actual mixed-scene Windows clients at vertical, gorilla and adult checkpoints."""
from pathlib import Path
import json
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
template=Path(__file__).with_name('capture_hakuna784_windows.py')
s=template.read_text().replace('build/hakuna784-windows','build/hakuna791-windows').replace('dist/installed-preview771/LionKing.exe','build/hakuna786/player.exe')
s=s.replace("((27000,5,ROOT/'build/hakuna778-checkpoint/entry.state'),(38000,6,ROOT/'build/hakuna781-native/38000.state'))", "((31000,5,ROOT/'build/hakuna790-route/31000/current.state'),(34500,5,ROOT/'build/hakuna790-route/34500/current.state'),(38000,6,ROOT/'build/hakuna781-native/38000.state'))")
s=s.replace("folder=out/str(level)","folder=out/str(frame)").replace("cases[str(level)]", "cases[str(frame)]")
s=s.replace("cmd.remove('--no-pace')", "cmd.remove('--no-pace')\n cmd[cmd.index('--asset-cache')+1]=str(ROOT/'build/hakuna787-helper/scenes.cache')\n cmd[cmd.index('--resource-profile')+1]=str(ROOT/f'build/hakuna789-player/{level}-md/resources.ini')")
exec(compile(s,str(template),'exec'))
p=ROOT/'build/hakuna791-windows/report.json';r=json.loads(p.read_text())
r['scope']='Actual private786 mixed-background Windows clients with prepared scene-v3 data; actor resource work remains incomplete.'
paths=[ROOT/'tools/capture_hakuna791_windows.py',template,ROOT/'build/hakuna786/build-report.json',ROOT/'build/hakuna787-helper/build-report.json']
r['source_sha256']={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
r['artifacts_sha256']={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}
p.write_text(json.dumps(r,indent=2)+'\n')
