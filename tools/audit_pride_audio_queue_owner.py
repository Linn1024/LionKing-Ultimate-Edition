"""Inspect accepted sound request provenance before designing annotations."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_loops.py')
source=original_verifier.read_text().replace('bounce-loop-observer','audio-queue-owner-observer')
source=source.replace('bounce-loop-audit','audio-queue-owner-audit')
source=source.replace('TLK_BOUNCE_LOOP_TRACE','TLK_AUDIO_QUEUE_OWNER').replace('loops.csv','queue.csv')
source=source.replace('native_bounce_loop_observer.c','native_audio_queue_owner_observer.c')
start=source.index("    columns=('scene'");end=source.index("    paths=[Path(__file__)",start)
source=source[:start]+'''    from collections import Counter
    differences={name:dict(Counter(row['command'] for row in rows)) for name,rows in runs.items()}
    accepted_bounces={name:[row for row in rows if row['command']=='8011'] for name,rows in runs.items()}
''' +source[end:]
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_audio_queue_owner_observer.py',bp,")
source=source.replace("original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},",
    "original_entry='c21c90',accepted_bounces=accepted_bounces,")
start=source.index("    print('Loops'");end=source.index('\n\n\nif __name__',start)
source=source[:start]+"    print('Accepted queue commands',differences,'bounce requests',{n:len(r) for n,r in accepted_bounces.items()},flush=True)"+source[end:]
exec(compile(source,str(original_verifier),'exec'))
