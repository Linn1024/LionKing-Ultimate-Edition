"""Read-only tracked host; inherited host object identity comes from actual compile."""
from pathlib import Path
original=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-animation52'","ROOT/'build/pride-menu-enable86'")
source=source.replace("== base/'host.obj'","== Path(previous['compiles']['host'][previous['compiles']['host'].index('-o')+1])")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
