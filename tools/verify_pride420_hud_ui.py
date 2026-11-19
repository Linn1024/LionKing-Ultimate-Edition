"""Actual SDL selection of one HUD child, live Apply and persistence."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride399_ui.py')
s=template.read_text();s=s[:s.index('    try:\n        initial=')]
s=s.replace('build/pride398/build-report.json','build/pride418/build-report.json').replace('build/pride399-ui','build/pride420-hud-ui')
s=s.replace("profile.write_text('schema = 1\\ngame = snes\\n')","profile.write_text('schema = 1\\ngame = snes\\ngraphics.hud.frames = md\\n')")
s=s.replace('trace=JsonPipe(',"i=cmd.index('--dump-window');del cmd[i:i+2]\ntrace=JsonPipe(")
s+='''    try:
        initial=wait(lambda r:r['about']==2 and r['field']==1500);hwnd=window_for(proc.pid);assert hwnd
        snapshots['initial']=initial;children=['graphics.hud.frames.'+k for k in ('roar','health','lives')]
        checks['whole_hud_inherited']=all(choices(initial)[name][1]==0 and choices(initial)[name][4]==2 for name in children)
        select(children[1]);key(0x0d);row=wait(lambda r:choices(r)[children[1]][1]==1);snapshots['draft']=row
        c=choices(row);checks['independent_draft']=c[children[1]][3]==1 and c[children[1]][4]==2 and all(c[name][3]==2 for name in (children[0],children[2]))
        capture_client(hwnd,out/'hud-options.png');key(0x71)
        after=wait(lambda r:not r['menu'] and r['field']>=1650 and r['health']>0);snapshots['after']=after
        capture_client(hwnd,out/'mixed-hud.png');c=choices(after)
        checks['applied_live']=after['field']>initial['field'] and c[children[1]][4]==1 and all(c[name][4]==2 for name in (children[0],children[2]))
        checks['persisted']='graphics.hud.frames.health = snes' in profile.read_text() and 'graphics.hud.frames = md' in profile.read_text()
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),template,reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,scope='Actual SDL child selection, inherited old whole-HUD source, independent draft, live Apply without restart, persistence and real Windows gameplay/client capture.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\\n')
print(checks,flush=True)
'''
exec(compile(s,str(template),'exec'))
