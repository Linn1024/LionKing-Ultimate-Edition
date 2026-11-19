"""Use the phase-corrected runtime with complete private reset cleanup."""
from pathlib import Path
from audit_scenes import ROOT
from summarize_pride_practice import bound

runtime_build_path=ROOT/'build/pride-reset/fixed4/build-report.json'
bound(runtime_build_path)
original_builder=ROOT/'tools/build_pride_machine_reset_player.py'
source=original_builder.read_text().replace("out=ROOT/'build/pride-machine-player'","out=ROOT/'build/pride-machine-player4'")
anchor="response=argv('response '+(base/'after.rsp').read_text())[1:];found=set()"
assert source.count(anchor)==1
source=source.replace(anchor,"response=argv('response '+(base/'after.rsp').read_text())[1:];response=[a.replace('build/pride-reset/fixed3/sdl-common_rtl.obj','build/pride-reset/fixed4/sdl-common_rtl.obj') for a in response];found=set()")
source=source.replace('sources=[Path(__file__),','sources=[Path(__file__),original_builder,runtime_build_path,')
exec(compile(source,str(original_builder),'exec'))
