"""Run combined level-only sound walkthrough after original-stream address qualification."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait567_route_audio.py')
s=template.read_text().replace('build/cant-wait565/build-report.json','build/cant-wait569/build-report.json').replace('build/cant-wait567-route-audio','build/cant-wait570-route-audio')
exec(compile(s,str(template),'exec'))
