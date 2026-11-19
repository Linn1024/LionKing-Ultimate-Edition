"""Current title checkpoints retain sounding MD menu effects and future commands."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-audio80';bp=base/'build-report.json';bound(bp)
    reference=ROOT/'build/pride-audio-dispatch75/report.json';prior=bound(reference)
    out=base/'resume';out.mkdir();checks={};commands={};end=900
    template=prior['command'].copy();template[0]=str(base/'player.exe');template[template.index('--frames')+1]=str(end)
    template[template.index('--hash-at')+1]=','.join(map(str,range(1,end+1)))
    profile=Path(template[template.index('--resource-profile')+1]).read_text()
    profile+='\n'+'\n'.join('audio.effects.'+key+' = md' for key in ('title_cursor','title_selection','options_adjustment','options_exit'))+'\n'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name,load=None,save=None,mode='aot'):
        folder=out/name;folder.mkdir();cmd=template.copy();(folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_text(profile)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if load:
            field,origin=load;cmd+=['--load',str(origin/'current.state')]
            row=next(json.loads(line) for line in (origin/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==field)
            origin_cmd=commands[origin.name];tape=Path(origin_cmd[origin_cmd.index('--input-polled')+1])
            remaining=folder/'remaining.polled.tape';remaining.write_bytes(tape.read_bytes()[row['poll_index']*2:]);cmd[cmd.index('--input-polled')+1]=str(remaining)
        if save:cmd+=['--save-at',str(save),str(folder/'current.state')]
        if mode=='lle':cmd+=['--lle']
        commands[name]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;print(name,rc,flush=True);return folder
    full=run('author592',save=592)
    after=run('author694',load=(592,full),save=694)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    allhashes=hashes(full);allpcm=pcm(full)
    checks['all900_reference_fields']=len(allhashes)==900
    checks['author694_remaining_guest_exact']=hashes(after)==[r for r in allhashes if int(r[0])>592]
    tail=pcm(after);checks['author694_pcm_suffix_exact']=bool(tail) and allpcm[-len(tail):]==tail
    for field,origin in ((592,full),(694,after)):
        identity=digest(origin/'current.state')
        for mode in ('aot','lle'):
            name=f'{field}-{mode}';folder=run(name,load=(field,origin),mode=mode)
            expected=[r for r in allhashes if int(r[0])>field]
            checks[name+'_remaining_guest_exact']=len(expected)==end-field and hashes(folder)==expected
            tail=pcm(folder);checks[name+'_sounding_pcm_suffix_exact']=bool(tail) and allpcm[-len(tail):]==tail
            for file in ('scene.json','window.png'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(full/file)
        checks[str(field)+'_state_unchanged']=digest(origin/'current.state')==identity
    paths=[Path(__file__),bp,reference]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                checkpoint_fields=[592,694],current_build_only=True,legacy_compatibility_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
