"""Full walk-through preservation on the route with no wall-wrapper calls."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_probe99_routes.py')
source=verifier_source.read_text().replace('pride-hyena-probe97','pride-hyena-probe103')
source=source.replace("checks[name+'_scoped_probe_behavior']=not rows if name=='native' else bool(rows) and all(int(r['selected_query_y'])==(int(r['native_query_y'])-8)&65535 for r in rows)","checks[name+'_no_probe_on_this_route']=not rows")
source=source.replace("('window.png','scene.json','audio.wav','probes.csv')","('window.png','scene.json','audio.wav')")
source=source.replace("paths=[Path(__file__),bp,reference]","paths=[Path(__file__),verifier_source,bp,reference,ROOT/'build/pride-hyena-probe101/report.json']")
source=source.replace('Headless; real window/UI and natural slope interactions remain separate.','Read-only101 confirms no wrapper callbacks on this completed route; actual callback activation is verified by the separate ordinary repeated-hit fight. Real window/UI and natural slope interactions remain separate.')
exec(compile(source,str(verifier_source),'exec'))
