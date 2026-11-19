"""Keep controller exploration near the intended climbing platforms."""
from pathlib import Path

score_planner=Path(__file__).with_name('pride_width_route_planner.py')
source=score_planner.read_text()
anchor="exec(compile(source,str(original_planner),'exec'))"
assert source.count(anchor)==1
source=source.replace(anchor,"""
source=source.replace("abs(v['x']-args.target_x)*.03", "abs(v['x']-args.target_x)*.5")
source=source.replace('(Path(__file__),original_planner)', '(Path(__file__),original_planner,score_planner)')
exec(compile(source,str(original_planner),'exec'))
""")
exec(compile(source,str(score_planner),'exec'))
