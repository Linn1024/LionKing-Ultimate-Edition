"""Native Options Off/On with independent MD adjustment output; no guest edits."""
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-output83';bp=base/'build-report.json';bound(bp)
    origin=base/'resume/report.json';prior=bound(origin);assert prior['result']=='PASS'
    stats=ROOT/'build/pride-menu-output84-isolation/report.json';s=bound(stats);assert s['result']=='PASS'
    out=ROOT/'build/pride-menu-enable85';out.mkdir();template=prior['commands']['author592'].copy()
    i=template.index('--save-at');del template[i:i+3]
    raw=Path(template[template.index('--input-polled')+1]).read_bytes()
    row=next(json.loads(x) for x in (origin.parent/'author592/tree.jsonl').read_text().splitlines() if json.loads(x)['field']==602)
    suffix=[]
    for button in (0x400,0x400,0x80,0x80):suffix += [0]*25+[button]
    tape=out/'ordinary.polled.tape';tape.write_bytes(raw[:row['poll_index']*2]+struct.pack('<'+'H'*len(suffix),*suffix)+bytes(8192))
    commands={};checks={};observations={}
    for name in ('native','adjustment'):
        folder=out/name;folder.mkdir();cmd=template.copy();cmd[0]=str(stats.parent/'player.exe');cmd[cmd.index('--input-polled')+1]=str(tape)
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        for key in ('title_cursor','title_selection','options_adjustment','options_exit'):profile+='\naudio.effects.'+key+' = snes\n'
        if name=='adjustment':profile+='\naudio.effects.options_adjustment = md\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_MENU_OUTPUT_STATS=str(folder/'output.csv'),TLK_SEMANTIC_OWNER_TRACE=str(folder/'owner.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        events=list(csv.DictReader((folder/'events.csv').open()));calls=[]
        for e in events:
            stack=bytes.fromhex(e['stack']);caller=int.from_bytes(stack[5:8],'little')+1 if e['return0']=='2d16' else 0
            if caller==0xc46a56:calls.append(e)
        checks[name+'_ordinary_off_on_calls']=rc==0 and len(calls)==2 and [r['fx_enabled'] for r in calls]==['0001','0000']
        output=list(csv.DictReader((folder/'output.csv').open()))
        observations[name]=dict(adjustments=calls,driver=list(csv.DictReader((folder/'driver.csv').open())),
                                muted_nonzero_samples=sum(int(r['nonzero_muted']) for r in output))
        commands[name]=cmd;print(name,checks,observations[name],flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    checks['all900_guest_fields_equal']=re.findall(pattern,(out/'native/run.log').read_text())==re.findall(pattern,(out/'adjustment/run.log').read_text())
    checks['only_one_selected_off_fm101']=[(r['selector'],r['value']) for r in observations['adjustment']['driver']]==[('2','101')]
    checks['selected_native_sounding_voice_removed']=observations['adjustment']['muted_nonzero_samples']>0
    paths=[Path(__file__),bp,origin,stats,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,ordinary_input_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
