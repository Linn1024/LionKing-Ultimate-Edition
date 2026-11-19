"""Test whether interpreter execution residue explains the early reset drift."""
from pathlib import Path

wrapped_diagnostic=Path(__file__).with_name('diagnose_pride_machine_reset.py')
source=wrapped_diagnostic.read_text().replace("out=base/'diagnostic'","out=base/'diagnostic-bridge'")
injection="source=original.read_text().replace('    __real_TlkResetMachine();', '    __real_TlkResetMachine();\\n    static uint8_t cold_bridge[1024];static unsigned have_cold_bridge;\\n    if(!have_cold_bridge) { interp_bridge_rb_state_save(cold_bridge);have_cold_bridge=1; }\\n    else interp_bridge_rb_state_load(cold_bridge);')"
source=source.replace('source=original.read_text()',injection)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),wrapped_diagnostic,')
exec(compile(source,str(wrapped_diagnostic),'exec'))
