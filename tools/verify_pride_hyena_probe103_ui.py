"""Actual new103 source restarts, MD then SNES, with fresh current-build seed."""
from pathlib import Path
wrapper=Path(__file__).with_name('verify_pride_hyena_probe100_ui2.py')
script=wrapper.read_text();anchor="exec(compile(script,str(wrapper),'exec'))";assert script.count(anchor)==1
script=script.replace(anchor,"script=script.replace(\"source=source.replace(\",\"source=source.replace(\",1)\n"+anchor)
# Expand the two inherited wrappers, adapting the final executable/output root.
target=Path(__file__).with_name('verify_pride_hyena_probe100_ui.py')
inner=target.read_text().replace('pride-hyena-probe97','pride-hyena-probe103')
call="exec(compile(source,str(verifier_source),'exec'))";assert inner.count(call)==1
inner=inner.replace(call,"source=source.replace(\"[(1,'snes'),(2,'md')]\",\"[(2,'md'),(1,'snes')]\")\nsource=source.replace('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/\"tools/verify_pride_hyena_probe100_ui.py\",')\n"+call)
exec(compile(inner,str(target),'exec'))
