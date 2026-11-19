"""Observe actual NPC action dispatches to separate idle loops from updates."""
from pathlib import Path

original_verifier=Path(__file__).with_name('audit_pride_bounce_loops.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-npc-observer3')
source=source.replace('bounce-loop-audit','bounce-npc-audit3')
source=source.replace('TLK_BOUNCE_LOOP_TRACE','TLK_BOUNCE_NPC_TRACE').replace('loops.csv','npc.csv')
source=source.replace('native_bounce_loop_observer.c','native_bounce_npc_observer3.c')
start=source.index("    columns=('scene'")
end=source.index("    paths=[Path(__file__)",start)
source=source[:start]+'''    columns=('actor','action','rng','input','raw_a0a','raw_1e03',
        'health','player_x','player_y','npc_bytes','player_bytes')
    differences={};phase_counts={}
    for phase in ('entry','return'):
        phases={name:[row for row in rows if row['phase']==phase] for name,rows in runs.items()}
        phase_counts[phase]={name:len(rows) for name,rows in phases.items()}
        differences[phase]={}
        for column in columns:
            rows=[dict(index=i+1,native_field=a['field'],bounce_field=b['field'],
                native=a[column],bounce=b[column])
                for i,(a,b) in enumerate(zip(phases['native'],phases['bounce'])) if a[column]!=b[column]]
            differences[phase][column]=dict(count=len(rows),first=rows[:3],last=rows[-3:])
''' +source[end:]
source=source.replace('paths=[Path(__file__),bp,',
    "paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_bounce_loop_observer.py',ROOT/'tools/build_pride_bounce_npc_observer3.py',bp,")
source=source.replace("original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},",
    "original_entry='c0abfb',original_return='c0abfe',phase_counts=phase_counts,")
start=source.index("    print('Loops'")
end=source.index('\n\n\nif __name__',start)
source=source[:start]+"    print('NPC actions',phase_counts,'differences',{p:{c:r['count'] for c,r in cols.items()} for p,cols in differences.items()},flush=True)"+source[end:]
exec(compile(source,str(original_verifier),'exec'))
