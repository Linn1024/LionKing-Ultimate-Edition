"""Build an ordinary stop-near-entrance tape from an observed native poll boundary."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';reference=base/'fights140/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/pride-hyena-entrance145-plan';out.mkdir()
cmd=r['commands']['native'];tape=Path(cmd[cmd.index('--input-polled')+1]);host=ROOT/'engine/build-win/tlk_headless.exe'
profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
command=[str(host),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--lle','--frames','3694','--input-polled',str(tape),'--resource-profile',str(profile),'--ram-log',str(out/'game.ram')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_WRAM_DUMP='3694',TLK_WRAM_DIR=str(out))
with (out/'run.log').open('wb') as log:rc=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
assert rc==0
log=(out/'run.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',log)[1]);prefix=tape.read_bytes()[:used*2]
ram_path=out/'hl_wram_3694.bin';ram=ram_path.read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
hashes={k:v for k,v in re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',log,re.M)}
frame=re.search(r'frame=3694 frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(reference.parent/'native/run.log').read_text());assert frame
checks=dict(original_boundary_matches_current_native_guest=hashes==dict(frame_sha256=frame[1],wram_sha256=frame[2]),pride_scene=word(0x1ff9e)==0 and int.from_bytes(ram[0xdf:0xe2],'little')==0xc00387)
for label,tail in [('stop',[0]*500),('slow',[0]*120+[0x100]*120+[0]*260)]:
    (out/(label+'.polled.tape')).write_bytes(prefix+struct.pack('<'+'H'*len(tail),*tail))
paths=[Path(__file__),reference,host,tape,profile,ROOT/'Lion King, The (USA).sfc']
(out/'report.json').write_text(json.dumps(dict(result='PLANNED' if all(checks.values()) else 'FAIL',checks=checks,command=command,polls=used,
    observed=dict(player=[word(0xb21b),word(0xb21d)],camera=[word(0xb29b),word(0xb29d)],hyena=[word(0xba1b),word(0xba1d)],timer=word(0xba3f)),
    scope='Fresh ordinary original-native prefix with a verified current-player guest boundary, followed only by neutral or right controller inputs. Does not yet prove a live countdown difference.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PLAN',checks,'polls',used,'player',[word(0xb21b),word(0xb21d)],'camera',[word(0xb29b),word(0xb29d)],flush=True)
