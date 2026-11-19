"""Follow accepted CPU packets into the original SPC parser, read-only."""
from pathlib import Path

original_verifier=Path(__file__).with_name('build_pride_spc_owner_observer.py')
template=original_verifier.read_text()
needle="exec(compile(source,str(original_verifier),'exec'))"
assert template.count(needle)==1
namespace={'__file__':__file__,'__name__':'_expand_only'}
exec(compile(template.replace(needle,''),str(original_verifier),'exec'),namespace)
source=namespace['source'].replace("out=base/'spc-owner-observer'","out=base/'audio-packet-observer2'")
source=source.replace('native_bounce_dsp_observer.c','native_audio_packet_observer2.c')
source=source.replace('native_spc_owner_trace.h','native_spc_packet_trace2.h')
source=source.replace("'  s_pride_spc_instruction=spc->pc;\\n'+needle", "'  PrideSpcPacketObserve(spc);\\n'+needle")
start=source.index("    needle='  apu_cpuWrite")
end=source.index("    dsp=out/'spc.c'",start)
source=source[:start]+source[end:]
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_spc_owner_observer.py',")
exec(compile(source,str(original_verifier),'exec'))
