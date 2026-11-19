"""Exercise the new walking probe choice through the actual Windows resource UI."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_music_ui65.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-music-output65'","ROOT/'build/pride-hyena-probe97'")
source=source.replace("source=base/'completion/report.json'","source=ROOT/'build/pride-menu-enable86/route/report.json'")
source=source.replace("cmd=prior['commands']['aot'].copy()","cmd=prior['commands']['menus-aot'].copy();cmd[0]=str(base/'player.exe')")
source=source.replace("node='audio.music.pride_lands'","node='gameplay.levels.pride_lands.hyena_probe_height'")
source=source.replace("r['field']>=1200 and r['descriptor']==0xc00387","r['field']>=2200 and r['descriptor']==0xc00387")
anchor="checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)";assert source.count(anchor)==1
source=source.replace(anchor,"checks[label+'_leaf_available']=next(c[-1] for c in snapshots[label+'-draft']['choices'] if c[0]==node)==choice")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
