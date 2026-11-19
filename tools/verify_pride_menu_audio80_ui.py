"""Real source tree, pause and restart for the independent title cursor choice."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_music_ui65.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-music-output65'","ROOT/'build/pride-menu-audio80'")
source=source.replace("base/'completion/report.json'","base/'route/report.json'")
source=source.replace("prior['commands']['aot']","prior['commands']['menus-aot']")
source=source.replace("node='audio.music.pride_lands'","node='audio.effects.title_cursor'")
source=source.replace("r['field']>=1200 and r['descriptor']==0xc00387","r['field']>=2200 and r['descriptor']==0xc00387")
anchor="checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)"
assert source.count(anchor)==1
source=source.replace(anchor,'# Menu synthesis and dispatch are verified separately by the full route gate.')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
