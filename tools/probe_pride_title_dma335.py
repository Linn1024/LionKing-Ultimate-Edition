"""Bypass only the DMA time charge, retaining the actual native byte engine."""
from pathlib import Path
template335=Path(__file__).with_name('probe_pride_title_dma334.py')
# Compose the frozen333 prototype with the334 power-on correction.
base=template335.with_name('probe_pride_title_dma333.py').read_text()
delta=template335.read_text()
prefix=delta[delta.index('source=template334.read_text()'):delta.index("exec(compile(source")]
scope={'template334':template335.with_name('probe_pride_title_dma333.py')}
exec(prefix,scope);source=scope['source']
source=source.replace('pride-title-dma334-probe','pride-title-dma335-probe')
source=source.replace('cpu_write8(cpu,cpu->DB,0x420b,mask);','dma_startDma(g_snes->dma,mask,0);')
source=source.replace("for label in ('control','batch'):","for label in ('batch',):")
source=source.replace('template334,bp','template335,bp')
exec(compile(source,str(template335),'exec'))
