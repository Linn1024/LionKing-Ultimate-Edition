"""Installed menu data errors must stop before gameplay with a Setup instruction."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu226-integrated/build-report.json';bound(build)
out=ROOT/'build/pride-menu254-assets';out.mkdir();checks={};commands={}
base=ref['command'].copy()
package=Path(base[base.index('--final-menu-assets')+1]);raw=package.read_bytes()
for name,data in (('truncated',raw[:-1]),('bad-version',raw[:8]+(999).to_bytes(4,'little')+raw[12:]),('checksum',raw[:-1]+bytes([raw[-1]^1]))):
    (out/(name+'.assets')).write_bytes(data)
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for art in ('snes','md'):
    for variant in ('missing','truncated','bad-version','checksum'):
        name=art+'-'+variant;folder=out/name;folder.mkdir();cmd=base.copy()
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            if flag=='--resource-profile':text=text.replace('graphics.pride_final_menu = md','graphics.pride_final_menu = '+art)
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        cmd[cmd.index('--final-menu-assets')+1]=str(out/(variant+'.assets'))
        cmd[cmd.index('--frames')+1]='1'
        cmd[cmd.index('--hash-at')+1]='1'
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        text=(folder/'run.log').read_text()
        checks[name+'_explicit_setup_error_before_gameplay']=rc==6 and 'Installed menu assets are missing or incompatible. Run Setup.' in text and 'frame=1 frame_sha256=' not in text
        print(name,rc,checks[name+'_explicit_setup_error_before_gameplay'],flush=True)
paths=[Path(__file__),reference,build,package]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Current226 required installed menu package: missing, truncated, invalid version and checksum corruption stop before guest field1 with explicit Setup error, for both artwork choices. No runtime ROM-decode substitute. Installer generation remains separately verified.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
