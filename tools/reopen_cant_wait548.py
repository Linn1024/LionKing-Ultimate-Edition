"""Restore the full second-level sound/gameplay scope without reopening settled graphics work."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait548-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','docs/HANDOFF.md','docs/second-level-goal.md','docs/cant-wait-delivery-review.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard545-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('cant-wait548-baseline')"))
p=ROOT/'docs/HANDOFF.md';s=p.read_text();s=s.replace('Current546,','Current548,',1);a=s.index('The first three practical playable milestones are');b=s.index('\n- Player:',a);s=s[:a]+'''The remaining Can't Wait to Be King sound/gameplay
goal is ACTIVE and takes priority over later levels. The user clarified that
earlier walkthrough/graphics milestones did not complete these sound choices.
Read [the restored scope](cant-wait-sound-gameplay-goal.md). Implement sounds;
change gameplay only for differences noticeable in ordinary play. Skip changes
that require code or instruments to notice. Public536 remains installed.
''' +s[b:];p.write_text(s)
p=ROOT/'docs/second-level-goal.md';s=p.read_text();s=s.replace('Status: practical playable milestone COMPLETE, preview482.', 'Status: remaining sound/gameplay work ACTIVE again by user direction. The\nearlier playable/graphics milestone, preview482, is retained as dated evidence.\nRead [restored scope](cant-wait-sound-gameplay-goal.md).');p.write_text(s)
print('SECOND_LEVEL_SOUND_GAMEPLAY_ACTIVE; public536 retained',flush=True)
