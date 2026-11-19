"""Check the real later-level launchers use installed ROMs and cache."""
from pathlib import Path
import subprocess,json,os,csv
r=Path(__file__).resolve().parents[1];d=r/'build/next-level-launchers';d.mkdir(exist_ok=True);config=d/'host.ini';config.write_text('opengl = 1\nscale = 2\n');results={}
for level,name,track in [(1,'Play Cant Wait Mix.cmd',2),(2,'Play Elephant Graveyard Mix.cmd',83),
                         (3,'Play Stampede Mix.cmd',145),(4,'Play Simbas Exile Mix.cmd',258),
                         (5,'Play Hakuna Matata Mix.cmd',40),(6,'Play Simbas Destiny Mix.cmd',281),
                         (7,'Play Be Prepared Mix.cmd',327),(8,'Play Simbas Return Mix.cmd',311),
                         (9,'Play Pride Rock Mix.cmd',432)]:
 env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(d/f'{level}-commands.csv')
 preset='final-levels.ini' if level>=7 else 'next-levels.ini'
 cmd=['cmd','/d','/c','call',str(r/name),'--config',str(config),'--resource-profile',str(r/'profiles'/preset),'--frames','2600','--no-pace','--no-audio','--no-record','--wav',str(d/f'{level}-start.wav'),'--wav-seconds','1','--dump-window',str(d/f'{level}.png'),'--dump-scene',str(d/f'{level}.json')]
 log=d/f'{level}.log'
 with log.open('wb') as f:subprocess.run(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
 scene=json.loads((d/f'{level}.json').read_text());assert scene['level']==level
 assert bool(scene['stage_detected'])==(level!=3),'Wrong scrolling/special-scene path'
 assert 'resource_cache=loaded' in log.read_text()
 commands=list(csv.DictReader((d/f'{level}-commands.csv').open()));assert any(row['selector']=='1' and int(row['value'])==track for row in commands)
 results[str(level)]={'launcher':name,'cached_imported_roms_used':True,'scene':scene['level'],'track':track};print(name,'actual installed launch PASS',flush=True)
(d/'report.json').write_text(json.dumps({'result':'PASS','levels':results},indent=2)+'\n')
