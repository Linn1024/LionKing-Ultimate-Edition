"""Observe native packet routing while retaining every full guest field."""
from pathlib import Path

original_verifier=Path(__file__).with_name('audit_pride_audio_queue_owner2.py')
template=original_verifier.read_text()
needle="exec(compile(source,str(original_verifier),'exec'))"
assert template.count(needle)==1
namespace={'__file__':__file__,'__name__':'_expand_only'}
exec(compile(template.replace(needle,''),str(original_verifier),'exec'),namespace)
source=namespace['source'].replace('audio-queue-owner-observer2','audio-packet-observer')
source=source.replace('audio-queue-owner-audit2','audio-packet-audit')
source=source.replace('native_audio_queue_owner_observer2.c','native_audio_packet_observer.c')
source=source.replace("TLK_AUDIO_QUEUE_OWNER=str(folder/'queue.csv'))",
    "TLK_AUDIO_QUEUE_OWNER=str(folder/'queue.csv'),TLK_AUDIO_TRANSFER_TRACE=str(folder/'transfer.csv'),TLK_SPC_PACKET_TRACE=str(folder/'spc.csv'))")
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_audio_packet_observer.py',ROOT/'tools/native_spc_packet_trace.h',")
exec(compile(source,str(original_verifier),'exec'))
