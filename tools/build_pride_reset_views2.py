"""Observe the second reset candidate with clean per-field host poll counters."""
from pathlib import Path

wrapped_builder = Path(__file__).with_name('build_pride_reset_views.py')
source = wrapped_builder.read_text().replace('build/pride-reset/fixed', 'build/pride-reset/fixed2').replace('build/pride-reset/views', 'build/pride-reset/views2')
source = source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),Path(wrapped_builder),')
source = source.replace('        generated=out/', "        source=source.replace('reset_audio_fraction=0;', 'reset_audio_fraction=0; s_polls_frame=0;')\n        generated=out/")
exec(compile(source, str(wrapped_builder), 'exec'))
