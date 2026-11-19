"""Actual independently selected entrance window, restart and pause/source isolation."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_music_ui65.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-music-output65'","ROOT/'build/pride-hyena-entrance139'")
source=source.replace("source=base/'completion/report.json'","source=ROOT/'build/pride-resource-tree118/routes99/report.json'")
source=source.replace("cmd=prior['commands']['aot'].copy()","cmd=prior['commands']['native'].copy();cmd[0]=str(base/'player.exe')")
source=source.replace("node='audio.music.pride_lands'","node='gameplay.levels.pride_lands.hyena_entrance_window'")
source=source.replace("[(1,'snes'),(2,'md')]","[(2,'md'),(1,'snes')]")
source=source.replace("r['field']>=1200 and r['descriptor']==0xc00387","r['field']>=2200 and r['descriptor']==0xc00387")
source=source.replace("def drivers():return list(csv.DictReader((out/'driver.csv').open()))","def drivers():return list(csv.DictReader((out/'driver.csv').open())) if (out/'driver.csv').exists() else []")
anchor="checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)"
assert source.count(anchor)==1
source=source.replace(anchor,"draft=next(c for c in snapshots[label+'-draft']['choices'] if c[0]==node)\n                checks[label+'_explicit_and_resolved_draft']=draft[1]==draft[3]==choice")
source=source.replace('device_audio_tested_separately=True','device_audio_not_tested=True')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
