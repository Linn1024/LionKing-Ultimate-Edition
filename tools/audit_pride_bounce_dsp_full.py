"""Observe native synthesis ownership before considering output-only replacement."""
from pathlib import Path
original_verifier=Path(__file__).with_name('audit_pride_bounce_loops.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-dsp-full-observer')
source=source.replace('bounce-loop-audit','bounce-dsp-full-audit')
source=source.replace('TLK_BOUNCE_LOOP_TRACE','TLK_BOUNCE_DSP_TRACE').replace('loops.csv','dsp.csv')
source=source.replace("str(folder/'dsp.csv'))","str(folder/'dsp.csv'),TLK_BOUNCE_DSP_DIR=str(folder),TLK_AUDIO_EVENTS=str(folder/'audio.csv'))")
source=source.replace('native_bounce_loop_observer.c','native_bounce_dsp_observer_full.c')
source=source.replace('4500','4500').replace('4501','4501').replace('actual==expected','actual==expected[:4500]')
start=source.index("    columns=('scene'");end=source.index("    paths=[Path(__file__)",start)
source=source[:start]+'''    differences={}
    for name,rows in runs.items():
        differences[name]={str(channel):dict(
            sources=sorted({int(r['srcn']) for r in rows if int(r['channel'])==channel}),
            peak=max(abs(int(r['sample'])) for r in rows if int(r['channel'])==channel),
            volumes=sorted({(int(r['volume_l']),int(r['volume_r'])) for r in rows if int(r['channel'])==channel}))
            for channel in range(8)}
''' +source[end:]
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/build_pride_bounce_dsp_full_observer.py',bp,")
source=source.replace("original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},",
    "snapshot_kind='read_only_dsp_after_frame',dsp_rows={n:len(r) for n,r in runs.items()},")
start=source.index("    print('Loops'");end=source.index('\n\n\nif __name__',start)
source=source[:start]+"    print('Native DSP observations',differences,flush=True)"+source[end:]
exec(compile(source,str(original_verifier),'exec'))
