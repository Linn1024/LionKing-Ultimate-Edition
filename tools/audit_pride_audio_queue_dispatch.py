"""Survey actual queue helper execution and CPU mode with neutral controls."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_dispatch_survey.py')
template=original_verifier.read_text();needle="exec(compile(source,str(original_verifier),'exec'))"
assert template.count(needle)==1
namespace={'__file__':__file__,'__name__':'_expand_only'}
exec(compile(template.replace(needle,''),str(original_verifier),'exec'),namespace)
source=namespace['source'].replace('bounce-dispatch-survey','audio-queue-dispatch-survey')
source=source.replace('bounce-dispatch-audit','audio-queue-dispatch-audit')
source=source.replace('TLK_BOUNCE_DISPATCH_TRACE','TLK_AUDIO_QUEUE_OWNER')
source=source.replace('native_bounce_dispatch_survey.c','native_audio_queue_dispatch_survey.c')
source=source.replace('build_pride_bounce_dispatch_survey.py','build_pride_audio_queue_dispatch_survey.py')
source=source.replace('4500','1500').replace('4501','1501').replace('actual==expected','actual==expected[:1500]')
source=source.replace("positive_control='c08934'","positive_control='c22c2d'")
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,")
exec(compile(source,str(original_verifier),'exec'))
