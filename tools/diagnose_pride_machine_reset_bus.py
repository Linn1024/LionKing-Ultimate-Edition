"""Test whether a retained AOT bus-charge accumulator explains reset drift."""
from pathlib import Path

wrapped_diagnostic=Path(__file__).with_name('diagnose_pride_machine_reset.py')
source=wrapped_diagnostic.read_text().replace("out=base/'diagnostic'","out=base/'diagnostic-bus'")
source=source.replace('out.mkdir();','out.mkdir(exist_ok=True);')
source=source.replace("source=original.read_text()", "source=original.read_text().replace('        inputs=0;', '        extern uint32_t g_aot_bus_mc;g_aot_bus_mc=0;inputs=0;')")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),wrapped_diagnostic,')
exec(compile(source,str(wrapped_diagnostic),'exec'))
