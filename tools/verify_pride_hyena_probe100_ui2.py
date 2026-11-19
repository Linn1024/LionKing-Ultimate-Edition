"""Switch resolved MD then SNES, retaining first unchanged-source UI attempt."""
from pathlib import Path
wrapper=Path(__file__).with_name('verify_pride_hyena_probe100_ui.py')
script=wrapper.read_text();anchor="exec(compile(source,str(verifier_source),'exec'))";assert script.count(anchor)==1
script=script.replace(anchor,"source=source.replace(\"out=base/'windows-ui'\",\"out=base/'windows-ui2'\").replace(\"[(1,'snes'),(2,'md')]\",\"[(2,'md'),(1,'snes')]\")\nsource=source.replace('paths=[Path(__file__),verifier_source,','paths=[Path(__file__),verifier_source,ROOT/\"tools/verify_pride_hyena_probe100_ui.py\",')\n"+anchor)
exec(compile(script,str(wrapper),'exec'))
