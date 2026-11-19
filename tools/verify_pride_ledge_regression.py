"""Keep preceding native/mixed/death behavior exact with ledge forwarding."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_scene_save_regression.py')
source=original.read_text().replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-ledge-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
source=source.replace('paths=[Path(__file__),build_path,',
    "paths=[Path(__file__),original,ROOT/'tools/pride_ledge_history.py',ROOT/'build/pride-ledge-baseline/report.json',build_path,")
exec(compile(source,str(original),'exec'))
