"""Check neutral dispatch coverage and both direct-page actor candidates."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_loops.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-dispatch-survey')
source=source.replace('bounce-loop-audit','bounce-dispatch-audit')
source=source.replace('TLK_BOUNCE_LOOP_TRACE','TLK_BOUNCE_DISPATCH_TRACE').replace('loops.csv','dispatch.csv')
source=source.replace('native_bounce_loop_observer.c','native_bounce_dispatch_survey.c')
start=source.index("    columns=('scene'");end=source.index("    paths=[Path(__file__)",start)
source=source[:start]+'''    from collections import Counter
    differences={name:dict(Counter(row['pc'] for row in rows)) for name,rows in runs.items()}
    matched={name:[row for row in rows if 'c58c68' in (row['global_descriptor'],row['dp_descriptor'])][:30]
        for name,rows in runs.items()}
''' +source[end:]
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_bounce_dispatch_survey.py',bp,")
source=source.replace("original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},",
    "positive_control='c08934',matching_descriptor_samples=matched,")
start=source.index("    print('Loops'");end=source.index('\n\n\nif __name__',start)
source=source[:start]+"    print('Dispatch coverage',differences,'matching samples',{n:len(r) for n,r in matched.items()},flush=True)"+source[end:]
exec(compile(source,str(original_verifier),'exec'))
