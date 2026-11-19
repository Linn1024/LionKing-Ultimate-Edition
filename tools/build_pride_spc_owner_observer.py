"""Trace original SPC writers using private host/SPC objects; no game edits."""
from pathlib import Path

original_verifier=Path(__file__).with_name('build_pride_bounce_output_prototype2.py')
source=original_verifier.read_text().replace("out=base/'bounce-output-prototype2'","out=base/'spc-owner-observer'")
source=source.replace("dsp_row=core('/dsp.c')","dsp_row=core('/spc.c')")
source=source.replace('native_bounce_npc_observer4.c','native_bounce_dsp_observer.c')
start=source.index('    original_dsp=Path(');end=source.index('    replacements={}',start)
source=source[:start]+'''    original_dsp=Path(dsp_row['file']);text=original_dsp.read_text()
    probe=ROOT/'tools/native_spc_owner_trace.h'
    needle='#include "apu.h"';assert text.count(needle)==1
    text=text.replace(needle,needle+'\\n#include "'+probe.as_posix()+'"')
    needle='  uint8_t opcode = spc_readOpcode(spc);';assert text.count(needle)==1
    text=text.replace(needle,'  s_pride_spc_instruction=spc->pc;\\n'+needle)
    needle='  apu_cpuWrite(spc->apu, adr, val);';assert text.count(needle)==1
    text=text.replace(needle,'  PrideSpcOwnerWrite(spc,adr,val);\\n'+needle)
    dsp=out/'spc.c';dsp.write_text(text)
    original_audio=Path(audio_row['file']);audio=original_audio
''' +source[end:]
source=source.replace("('audio',audio_row,audio)","('unused_audio',audio_row,audio)")
source=source.replace("for label,row,source in (('host',host_row,host),('dsp',dsp_row,dsp),('unused_audio',audio_row,audio)):",
    "for label,row,source in (('host',host_row,host),('spc',dsp_row,dsp)):")
source=source.replace('replacement_object_count=3','replacement_object_count=2')
source=source.replace('prototype_sample=92','read_only_spc_observation=True')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,probe,bp,")
source=source.replace('Private output prototype built; production unchanged; ownership scope still unproven','Private SPC writer observer built; production unchanged')
exec(compile(source,str(original_verifier),'exec'))
