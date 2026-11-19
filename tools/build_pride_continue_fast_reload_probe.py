"""Build a read-only observer for the visible Continue exit discrepancy."""
from pathlib import Path

original = Path(__file__).with_name('build_pride_final_input_refresh_probe.py')
source = original.read_text()
for before, after in [
    ('build/pride-final-input-refresh-probe2', 'build/pride-continue-fast-reload-probe'),
    ('tools/pride_final_input_refresh_probe.c', 'tools/pride_continue_fast_reload_probe.c'),
    ('ROOT/"tools/build_pride_final_input_probe.py",',
     'ROOT/"tools/build_pride_final_input_probe.py",ROOT/"tools/build_pride_final_input_refresh_probe.py",ROOT/"tools/pride_final_input_refresh_probe.c",'),
]:
    assert source.count(before) == 1, before
    source = source.replace(before, after)
exec(compile(source, str(original), 'exec'))
