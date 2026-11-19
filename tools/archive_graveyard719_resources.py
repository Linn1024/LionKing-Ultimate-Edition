"""Recover the exact prior resource source, verified against the frozen build."""
import hashlib,json
from audit_scenes import ROOT
out=ROOT/'build/graveyard719-resource-baseline';out.mkdir(exist_ok=True)
name='engine/runner/tlk_resources.c';s=(ROOT/name).read_text()
s=s.replace('           TlkResourcesUseMd("graphics.sprites.simba.cub.graveyard_death_motion") ||\n','')
a=s.index('        if(!strcmp(nodes[i].id,"graphics.sprites.simba.cub.graveyard_death_motion") &&');b=s.index('        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.hyena_ground_tags")',a);s=s[:a]+s[b:]
s=s.replace(' ||\n             !strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.hyena_bounds")','')
expected=json.loads((ROOT/'build/graveyard708/build-report.json').read_text())['source_sha256'][name]
# The maintained files use LF; verify bytes rather than silently accepting reconstruction.
data=s.replace('\n','\r\n').encode();assert hashlib.sha256(data).hexdigest()==expected
q=out/name;q.parent.mkdir(parents=True);q.write_bytes(data)
(out/'report.json').write_text(json.dumps(dict(historical_sources={name:dict(sha256=expected,archive=q.relative_to(ROOT).as_posix())}),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('graveyard718-doc-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('graveyard719-resource-baseline')"));print('ARCHIVED',expected)
