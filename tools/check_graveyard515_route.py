"""Run the full Graveyard from the recording-compatible current entry, with all implemented resources."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard506_route.py')
s=template.read_text().replace('build/graveyard505-entry/report.json','build/graveyard511-checkpoint/report.json').replace('build/graveyard506-route','build/graveyard515-route')
a=s.index("seed=r['command'].copy()");b=s.index('trace=JsonPipe',a)
s=s[:a]+'''# Current recorded entry carries naturally earned upgrades and original RNG.
(out/'host.ini').write_text('opengl = 0\\nscale = 3\\n')
(out/'resources.ini').write_bytes((ROOT/'build/graveyard505-entry/resources.ini').read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
cmd=r['command'].copy()
for flag,count in (('--save-at',3),('--input-polled',2)):
    i=cmd.index(flag);del cmd[i:i+count]
cmd+=['--load',str(reference.parent/'entry.state'),'--input-polled',str(tape),'--wav',str(out/'audio.wav'),'--wav-seconds','1']
for flag,value in (('--frames','19400'),('--hash-at','13500,15500,18000'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
''' +s[b:]
s=s.replace("row['field']>1600", "row['field']>13200").replace("('opening',2000),('middle',4000),('late',6500)", "('opening',13500),('middle',15500),('late',17800)")
s=s.replace("list(csv.DictReader((out/'entry-music.csv').open()))+", '')
s=s.replace('direct_level_select=True', 'current_recorded_entry=True').replace('command=cmd,seed_command=seed,','command=cmd,')
s=s.replace('paths=[Path(__file__),reference', 'paths=[Path(__file__),template,ROOT/\'build/graveyard505-entry/resources.ini\',reference')
exec(compile(s,str(template),'exec'))
