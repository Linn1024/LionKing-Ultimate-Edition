"""Recover prior catalog bytes by removing only the reviewed53 appended records."""
import json,re,hashlib
from audit_scenes import ROOT
out=ROOT/'build/next744-sprite-map-baseline';out.mkdir();name='engine/generated/resources/pride_sprite_map.h'
new={int(r['snes'],16)&0x3fffff for r in json.loads((ROOT/'tools/next_scene_pairs.json').read_text())['pairs']}
text=(ROOT/name).read_text();lines=[];removed=0
for line in text.splitlines(keepends=True):
 match=re.match(r'\{0x([0-9a-f]+),',line)
 if match and int(match[1],16) in new:removed+=1
 else:lines.append(line)
assert removed==53
data=''.join(lines).replace('\n','\r\n').encode();expected=json.loads((ROOT/'build/graveyard720/build-report.json').read_text())['source_sha256'][name]
assert hashlib.sha256(data).hexdigest()==expected
q=out/name;q.parent.mkdir(parents=True);q.write_bytes(data)
(out/'report.json').write_text(json.dumps(dict(historical_sources={name:dict(sha256=expected,archive=q.relative_to(ROOT).as_posix())}),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next742-audio-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next744-sprite-map-baseline')"));print('ARCHIVED exact old catalog')
