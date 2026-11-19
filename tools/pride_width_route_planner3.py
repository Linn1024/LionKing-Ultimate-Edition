"""Explore longer ordinary jump holds while keeping the intended climbing area."""
from pathlib import Path

author_planner=Path(__file__).with_name('pride_width_route_planner.py')
source=author_planner.read_text()
anchor="exec(compile(source,str(original_planner),'exec'))"
assert source.count(anchor)==1
source=source.replace(anchor,"""
source=source.replace('hold=min(12,step//3)', 'hold=min(24,step-14)')
source=source.replace("abs(v['x']-args.target_x)*.03", "abs(v['x']-args.target_x)*.15")
source=source.replace('(Path(__file__),original_planner)', '(Path(__file__),original_planner,author_planner)')
exec(compile(source,str(original_planner),'exec'))
""")
exec(compile(source,str(author_planner),'exec'))
