"""Keep original display initialization, then test the later final-life bypass."""
from pathlib import Path

original=Path(__file__).with_name('probe_pride_final_skip.py')
source=original.read_text()
changes={
    "ROOT/'build/pride-final-skip'":"ROOT/'build/pride-final-skip-late'",
    "ROOT/'build/pride-bounce-owner-work/player/final-skip-probe'":
        "ROOT/'build/pride-bounce-owner-work/player/final-skip-late-probe'",
    'TLK_FINAL_SKIP=str(int(skip))':"TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP=str(int(skip))",
    "paths=[Path(__file__),ROOT/'tools/pride_final_skip_probe.c',bp":
        "paths=[Path(__file__),original,ROOT/'tools/pride_final_skip_probe.c',ROOT/'tools/pride_final_skip_late_probe.c',bp",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
