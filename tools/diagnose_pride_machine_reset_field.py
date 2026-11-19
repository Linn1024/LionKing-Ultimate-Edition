"""Test the machine-owned short-field and late-NMI phase at reboot."""
from pathlib import Path

wrapped_diagnostic=Path(__file__).with_name('diagnose_pride_machine_reset.py')
source=wrapped_diagnostic.read_text().replace("out=base/'diagnostic'","out=base/'diagnostic-field'")
reset='''        extern int tlk_snes_short_field_get(void);
        extern int tlk_snes_late_nmi_get(void);
        extern void tlk_snes_short_field_set(int);
        extern void tlk_snes_late_nmi_set(int);
        printf("reset_beam_phase,%d,%d\\n",tlk_snes_short_field_get(),tlk_snes_late_nmi_get());
        tlk_snes_short_field_set(0);tlk_snes_late_nmi_set(0);
        inputs=0;'''
source=source.replace('source=original.read_text()',"source=original.read_text().replace('        inputs=0;',"+repr(reset)+")")
source=source.replace('out.mkdir();','out.mkdir(exist_ok=True);')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),wrapped_diagnostic,')
exec(compile(source,str(wrapped_diagnostic),'exec'))
