"""Wait for the processed mouse event and check editor re-entry.

This diagnostic tested an event-delivery-delay hypothesis. It still timed out;
elapsed time was not the cause. The later mouse-queue verifier delivers motion
and click together and passes. Retain this failed diagnostic for provenance.
"""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_soft_tree.py')
source=original_verifier.read_text()
source=source.replace("out=base/'windows'/args.case","out=base/'windows-wait'/args.case")
source=source.replace("time.sleep(.1)\n                row=latest(trace);checks['mouse_after_resize']", "wait(lambda r:choice(r,'display.viewport')[1]==0 and r['dirty']==1)\n                row=latest(trace);checks['mouse_after_resize']")
source=source.replace("                key(0x1b)  # leave Resources section\n                key(0x1b)  # close settings", """                key(0x0d)
                row=wait(lambda r:r['about']==2)
                checks['reopen_applied_choices']=row['dirty']==0 and profile.read_bytes()==saved and all(c[1]==c[2] for c in row['choices'])
                snap('reopened')
                key(0x7b)  # F12 closes the entire editor/settings window""")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
