"""Fresh runs retain the independently selected hyena entry voice from public72."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-lizard-voice74';bp=base/'build-report.json';bound(bp)
    source=ROOT/'build/pride-hyena-voice72/voice-fight/report.json';prior=bound(source)
    out=base/'hyena-regression';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for name in ('md-aot','md-lle'):
        folder=out/name;folder.mkdir();cmd=prior['commands'][name].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[name]=cmd
        env=dict(clean,TLK_HYENA_VOICE_TRACE=str(folder/'entries.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        reference=source.parent/name
        actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(reference/'run.log').read_text())
        checks[name+'_exit']=rc==0
        checks[name+'_all4600_guest_fields_retained']=len(actual)==4600 and actual==expected
        for file in ('audio.wav','scene.json','window.png','entries.csv','driver.csv'):checks[name+'_'+file+'_retained']=digest(folder/file)==digest(reference/file)
        entries=list(csv.DictReader((folder/'entries.csv').open()));checks[name+'_three_hyena_voices']=len(entries)==3 and all(r['emitted']=='1' for r in entries)
        print(name,rc,flush=True)
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,fresh_boots_only=True,old_save_compatibility_not_tested=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
