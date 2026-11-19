"""Check visible line placement, falling letters, narrow width and Pride control."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/level-caption345/build-report.json';bound(build)
out=ROOT/'build/level-caption347';out.mkdir(exist_ok=True);commands={};checks={}
ref=bound(ROOT/'build/level-caption346/report.json');assert ref['result']=='PASS'
pride=json.loads((ROOT/'build/pride-caption270-clamp/report.json').read_text())['commands']['320-md-1050-new']
assets=json.loads((ROOT/'build/pride-porcupine328/report.json').read_text())['commands']['native-new']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
for case,template,width,field in [('falling',ref['command'],320,1530),('narrow',ref['command'],256,1550),('pride',pride,320,1050)]:
    for version in ('old','new'):
        label=case+'-'+version;folder=out/label;folder.mkdir(exist_ok=True);cmd=template.copy()
        cmd[0]=str(ROOT/('build/pride-porcupine327/player.exe' if version=='old' else 'build/level-caption345/player.exe'))
        for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
            (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
        with (folder/'resources.ini').open('a') as f:f.write('\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        cmd[cmd.index('--frames')+1]=str(field);cmd[cmd.index('--hash-at')+1]=str(field)
        for flag in ('--caption-assets','--checkpoint-assets','--revival-assets','--native-hud-assets'):
            if flag not in cmd:cmd+=[flag,assets[assets.index(flag)+1]]
        for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/name)
        if '--wav' in cmd:
            i=cmd.index('--wav');del cmd[i:i+2]
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[label]=cmd;checks[label+'_exit']=rc==0
    a=out/(case+'-old');b=out/(case+'-new');pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    checks[case+'_guest']=bool(re.findall(pattern,(a/'run.log').read_text())) and re.findall(pattern,(a/'run.log').read_text())==re.findall(pattern,(b/'run.log').read_text())
    checks[case+'_scene']=digest(a/'scene.json')==digest(b/'scene.json')
    checks[case+'_picture']= (digest(a/'window.png')==digest(b/'window.png'))==(case=='pride')
    print(case,{k:v for k,v in checks.items() if k.startswith(case)},flush=True)
# Verify the actual unchanged font pixels translated24 native pixels left.
old=ROOT/'build/level-caption341/2';new=ROOT/'build/level-caption346'
r=json.loads((old/'scene.json').read_text());colors={((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31) for v in r['obj_palette0'][1:]}
images=[Image.open(p/'window.png').convert('RGB') for p in (old,new)]
mask=lambda im,y0,y1:{(x,y) for y in range(y0,y1) for x in range(80,600) if im.getpixel((x,y)) in colors}
a,b=[mask(im,96,128) for im in images];checks['first_line_exact_24_pixel_translation']=bool(a) and {(x-48,y) for x,y in a}==b
checks['second_line_pixels_unchanged']=mask(images[0],128,160)==mask(images[1],128,160)
paths=[Path(__file__),build,ROOT/'build/level-caption346/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='Visible Elephant Graveyard per-line centring at both widths and while falling, exact glyph translation; Pride MD-art control unchanged. Guest state preserved. No unrelated level/gameplay suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
