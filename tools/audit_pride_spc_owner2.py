"""Capture SPC ownership after expanding the frozen DSP verifier template."""
from pathlib import Path

original_verifier=Path(__file__).with_name('audit_pride_bounce_dsp.py')
template=original_verifier.read_text()
needle="exec(compile(source,str(original_verifier),'exec'))";assert template.count(needle)==1
namespace={'__file__':__file__,'__name__':'_expand_only'}
exec(compile(template.replace(needle,''),str(original_verifier),'exec'),namespace)
source=namespace['source'].replace('bounce-dsp-observer','spc-owner-observer')
source=source.replace('bounce-dsp-audit','spc-owner-audit')
source=source.replace("TLK_AUDIO_EVENTS=str(folder/'audio.csv'))", "TLK_AUDIO_EVENTS=str(folder/'audio.csv'),TLK_SPC_OWNER_WRITES=str(folder/'spc-writes.csv'))")
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,ROOT/'tools/native_spc_owner_trace.h',ROOT/'tools/build_pride_spc_owner_observer.py',")
exec(compile(source,str(original_verifier),'exec'))
