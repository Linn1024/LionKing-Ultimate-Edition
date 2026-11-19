"""Capture original SPC writer provenance with full guest-state controls."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_dsp.py')
source=original_verifier.read_text().replace('bounce-dsp-observer','spc-owner-observer')
source=source.replace('bounce-dsp-audit','spc-owner-audit')
source=source.replace('build_pride_bounce_dsp_observer.py','build_pride_spc_owner_observer.py')
source=source.replace("TLK_AUDIO_EVENTS=str(folder/'audio.csv'))", "TLK_AUDIO_EVENTS=str(folder/'audio.csv'),TLK_SPC_OWNER_WRITES=str(folder/'spc-writes.csv'))")
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,ROOT/'tools/native_spc_owner_trace.h',")
exec(compile(source,str(original_verifier),'exec'))
