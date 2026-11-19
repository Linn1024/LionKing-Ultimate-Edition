"""Read-only whole-game observer for the physical music-tail candidate."""
from pathlib import Path
original=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'", "ROOT/'build/pride-music-output65'")
source=source.replace("previous['compiles']['host']", "host_build['compiles']['host']")
source=source.replace("base/'host.obj'", "ROOT/'build/pride-checkpoint-animation52/host.obj'")
source=source.replace("base/'allbugs-observer'", "base/'allbugs-observer2'")
anchor='    previous = bound(source_report)';assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\n    host_report=ROOT/'build/pride-checkpoint-animation52/build-report.json'\n    host_build=bound(host_report)")
source=source.replace('paths = [Path(__file__),', 'paths = [Path(__file__),original,host_report,')
exec(compile(source,str(original),'exec'))
