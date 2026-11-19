"""Allow the normal bonus stage and next-level loader to finish; save an endpoint for reuse."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard515_route.py')
s=template.read_text().replace('build/graveyard515-route','build/graveyard516-route').replace("('--frames','19400')", "('--frames','19800')")
s=s.replace("exec(compile(s,str(template),'exec'))", "s=s.replace('trace=JsonPipe',\"cmd+=['--save-at','19400',str(out/'endpoint.state')]\\ntrace=JsonPipe\")\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))
