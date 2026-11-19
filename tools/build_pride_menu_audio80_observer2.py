"""Track candidate80 using its actual inherited host object identity."""
from pathlib import Path
original=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'","ROOT/'build/pride-menu-audio80'")
source=source.replace("base/'allbugs-observer'","base/'allbugs-observer2'")
source=source.replace("== base/'host.obj'","== Path(previous['compiles']['host'][previous['compiles']['host'].index('-o')+1])")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
