"""Run ordinary-host gates after correcting retained short-field phase."""
from pathlib import Path

wrapped_native_tool=Path(__file__).with_name('verify_pride_reset_native.py')
source=wrapped_native_tool.read_text().replace('build/pride-reset/fixed2','build/pride-reset/fixed4')
source=source.replace("'Path(__file__),original,build_path'", "'Path(__file__),wrapped_native_tool,original,build_path'")
exec(compile(source,str(wrapped_native_tool),'exec'))
