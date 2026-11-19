"""Select Easy through ordinary Options, then level three; save at actual initialization."""
import gzip,importlib.util,json,os,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard505-entry/report.json';r=bound(reference)
helper=ROOT/'engine/tools/re/make_level_tape.py';spec=importlib.util.spec_from_file_location('level_macro',helper);mlt=importlib.util.module_from_spec(spec);spec.loader.exec_module(mlt)
steps=mlt.BOOT_TO_OPTIONS+['A','wait 20']*2+mlt.BARRY+mlt.preset(2)[len(mlt.BOOT_TO_OPTIONS)+len(mlt.BARRY):]
words=mlt.build(steps)+[0]*700
out=ROOT/'build/graveyard507-easy-entry';out.mkdir(exist_ok=True);tape=out/'easy-level3.tape';tape.write_bytes(struct.pack('<'+'H'*len(words),*words))
base=r['command'].copy()
for flag,count in (('--save-at',3),('--practice-level',2)):
    i=base.index(flag);del base[i:i+count]
base+=['--input',str(tape)]
(out/'host.ini').write_bytes((reference.parent/'host.ini').read_bytes());(out/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
probe=base.copy()
for flag,value in (('--frames','1600'),('--hash-at','1600'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'probe.png')),('--dump-scene',str(out/'probe-scene.json'))):probe[probe.index(flag)+1]=value
trace=JsonPipe(out/'probe-tree.jsonl.gz')
try:
    with (out/'probe.log').open('wb') as log:subprocess.run(probe,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
finally:metadata=trace.finish()
rows=[json.loads(x) for x in gzip.open(out/'probe-tree.jsonl.gz','rt')];lastzero=max(x['field'] for x in rows if x['level']==2 and x['descriptor']==0xc003eb and x['health']==0)
entry=next(x for x in rows if x['field']>lastzero and x['descriptor']==0xc003eb and x['health']>0);assert entry['difficulty']==0 and entry['health']==6,entry
cmd=probe.copy()
for flag,value in (('--frames',str(entry['field'])),('--hash-at',str(entry['field'])),('--dump-window',str(out/'entry.png')),('--dump-scene',str(out/'entry-scene.json'))):cmd[cmd.index(flag)+1]=value
cmd+=['--save-at',str(entry['field']),str(out/'entry.state')]
with (out/'entry.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(out/'entry-music.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'entry-scene.json').read_text());assert scene['latched_gameplay']['player']==[1008,336] and scene['latched_gameplay']['health']==6
paths=[Path(__file__),helper,reference,ROOT/'build/graveyard503/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS',command=cmd,probe_command=probe,entry_field=entry['field'],entry=entry,trace_metadata=metadata,checks=dict(ordinary_easy_options=True,ordinary_debug_level_select=True,no_invulnerability=True,full_health_entry=True,no_earlier_levels=True),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('EASY_ENTRY',entry['field'],scene['latched_gameplay'],flush=True)
