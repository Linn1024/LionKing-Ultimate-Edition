"""Private read-only DSP ownership census at the actual sample cadence."""
from pathlib import Path
original_verifier=Path(__file__).with_name('build_pride_bounce_output_prototype2.py')
source=original_verifier.read_text().replace("out=base/'bounce-output-prototype2'","out=base/'dsp-owner-sample-observer'")
source=source.replace('native_bounce_npc_observer4.c','native_spc_voice_owner_observer.c')
start=source.index('    original_dsp=Path(');end=source.index('    replacements={}',start)
source=source[:start]+'''    original_dsp=Path(dsp_row['file']);text=original_dsp.read_text()
    probe=ROOT/'tools/native_dsp_owner_sample_trace.h'
    needle='#include "apu.h"';assert text.count(needle)==1
    text=text.replace(needle,needle+'\\n#include "'+probe.as_posix()+'"')
    needle='    dsp_cycleChannel(dsp, i);';assert text.count(needle)==1
    text=text.replace(needle,needle+'\\n    PrideDspOwnerSample(dsp,i);')
    dsp=out/'dsp.c';dsp.write_text(text)
    original_audio=Path(audio_row['file']);audio=original_audio
''' +source[end:]
source=source.replace("for label,row,source in (('host',host_row,host),('dsp',dsp_row,dsp),('audio',audio_row,audio)):",
    "for label,row,source in (('host',host_row,host),('dsp',dsp_row,dsp)):")
source=source.replace('replacement_object_count=3','replacement_object_count=2')
source=source.replace('prototype_sample=92','read_only_dsp_observation=True')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,probe,bp,")
source=source.replace('Private output prototype built; production unchanged; ownership scope still unproven','Private per-sample ownership observer built; production unchanged')
exec(compile(source,str(original_verifier),'exec'))
