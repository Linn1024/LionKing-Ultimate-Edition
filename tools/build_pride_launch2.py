"""Bypass the complete wrapper chain in native mode and virtualize repeat dirs."""
from pathlib import Path

first_builder=Path(__file__).with_name('build_pride_launch.py')
source=first_builder.read_text().replace("ROOT/'build/pride-launch'","ROOT/'build/pride-launch2'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),first_builder,')
source=source.replace('for p in (Path(__file__),ROOT/', 'for p in (Path(__file__),first_builder,ROOT/')
source=source.replace("text=text.replace('_mkdir(folder)','TlkPrideMakeDirectory(folder)')", "text=text.replace('_mkdir(folder)','TlkPrideMakeDirectory(folder)').replace('_mkdir(repeat_debug_folder)','TlkPrideMakeDirectory(repeat_debug_folder)')")
needle="    anchor='preparation_frame(uint32 inputs) {\\n';"
assert source.count(needle)==1
source=source.replace(needle,"    anchor='component_frame(uint32 inputs) {\\n';assert text.count(anchor)==1;text=text.replace(anchor,anchor+'    if(!TlkPrideHealthDeathSelected())return RtlRunFrame(inputs);\\n')\n"+needle)
exec(compile(source,str(first_builder),'exec'))
