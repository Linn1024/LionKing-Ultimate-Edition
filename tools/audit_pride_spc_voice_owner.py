"""Capture full-route native software-voice ownership with neutral controls."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_dsp.py')
template=original_verifier.read_text();needle="exec(compile(source,str(original_verifier),'exec'))"
assert template.count(needle)==1
namespace={'__file__':__file__,'__name__':'_expand_only'}
exec(compile(template.replace(needle,''),str(original_verifier),'exec'),namespace)
source=namespace['source'].replace('bounce-dsp-observer','spc-voice-owner-observer')
source=source.replace('bounce-dsp-audit','spc-voice-owner-audit')
source=source.replace('native_bounce_dsp_observer.c','native_spc_voice_owner_observer.c')
source=source.replace('build_pride_bounce_dsp_observer.py','build_pride_spc_voice_owner_observer.py')
source=source.replace('1500','4500').replace('1501','4501')
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,")
exec(compile(source,str(original_verifier),'exec'))
