"""Aggregate focused skull proof and preservation of all prior installed gameplay records."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
proofs=[ROOT/'build/graveyard685-skull/report.json',ROOT/'build/graveyard686-setup/report.json',ROOT/'build/graveyard687-window/report.json'];checks={p.parent.name:bound(p)['result']=='PASS' for p in proofs}
def sections(p):
 raw=p.read_bytes();at=192+416+17792
 for _ in range(struct.unpack_from('<I',raw,20)[0]):
  _,a,b=struct.unpack_from('<III',raw,at);at+=12+a+b
 data=raw[at:];version=struct.unpack_from('<I',data,8)[0];n=4 if version==1 else 5;at=32 if n==4 else 40;result=[]
 for i in range(n):
  size=struct.unpack_from('<I',data,16+i*4)[0];result.append(data[at:at+size]);at+=size
 assert at==len(data);return result
old=ROOT/'build/graveyard619-helper/sprites.assets';new=ROOT/'build/graveyard683-helper/sprites.assets';a=sections(old);b=sections(new)
checks.update(all_prior_start_reactivation_hitbox_roar_data_exact=a==b[:4],new_installed_terrain_tags=len(b)==5 and b[4][:8]==b'TLKGYT01',terrain_size=len(b[4])==62416)
out=ROOT/'build/graveyard688-qualified';out.mkdir(exist_ok=True);paths=[Path(__file__),*proofs,ROOT/'build/graveyard684/build-report.json',ROOT/'build/graveyard683-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='Opening skull: native guest/window control, independent socket artwork/colors, 11 exact original MD images, matching jump starts/landings and synchronization, real Windows captures, actual isolated Setup; all prior gameplay payloads exact. No full-level or general AI parity claim. No unrelated death/audio/tape reruns.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
