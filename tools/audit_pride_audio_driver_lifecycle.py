"""Observe queue reset, rejection, completed transport and SPC upload seams."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_loops.py')
source=original_verifier.read_text().replace('bounce-loop-observer','audio-driver-lifecycle-observer')
source=source.replace('bounce-loop-audit','audio-driver-lifecycle-audit')
source=source.replace('TLK_BOUNCE_LOOP_TRACE','TLK_AUDIO_DRIVER_TRACE').replace('loops.csv','lifecycle.csv')
source=source.replace("TLK_AUDIO_DRIVER_TRACE=str(folder/'lifecycle.csv'))",
    "TLK_AUDIO_DRIVER_TRACE=str(folder/'lifecycle.csv'),TLK_AUDIO_DRIVER_DIR=str(folder))")
source=source.replace('native_bounce_loop_observer.c','native_audio_driver_lifecycle_observer.c')
start=source.index("    columns=('scene'");end=source.index("    paths=[Path(__file__)",start)
source=source[:start]+'''    from collections import Counter
    differences={name:dict(Counter(row['pc'] for row in rows)) for name,rows in runs.items()}
''' +source[end:]
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_audio_driver_lifecycle_observer.py',bp,")
source=source.replace("original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},",
    "original_entry='multiple_original_driver_seams',record_counts={n:len(r) for n,r in runs.items()},")
start=source.index("    print('Loops'");end=source.index('\n\n\nif __name__',start)
source=source[:start]+"    print('Driver lifecycle records',report['record_counts'],'PC counts',differences,flush=True)"+source[end:]
exec(compile(source,str(original_verifier),'exec'))
