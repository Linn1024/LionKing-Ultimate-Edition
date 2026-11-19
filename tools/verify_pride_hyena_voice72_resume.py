"""Current-build checkpoints immediately before/after entry and during the voice."""
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
    base=ROOT/'build/pride-hyena-voice72';bp=base/'build-report.json';bound(bp)
    source=ROOT/'build/pride-music-output65/hyena-effects/report.json';prior=bound(source)
    out=base/'voice-resume';out.mkdir();checks={};commands={};folders={}
    template=prior['commands']['native'].copy();template[0]=str(base/'player.exe')
    profile=Path(template[template.index('--resource-profile')+1]).read_text()+'\naudio.effects.world.hyena_hurt = md\n'
    tape=Path(template[template.index('--input-polled')+1]);clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name,load=None,save=None,mode='aot'):
        folder=out/name;folder.mkdir();cmd=template.copy();(folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_text(profile)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if load:
            state,field,origin=load;cmd+=['--load',str(state)]
            row=next(json.loads(line) for line in (origin/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==field)
            remaining=folder/'remaining.polled.tape';remaining.write_bytes(tape.read_bytes()[row['poll_index']*2:]);cmd[cmd.index('--input-polled')+1]=str(remaining)
        if save:cmd+=['--save-at',str(save),str(folder/'current.state')]
        if mode=='lle':cmd+=['--lle']
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_HYENA_VOICE_TRACE=str(folder/'entries.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;folders[name]=folder;print(name,rc,flush=True);return folder
    full=run('author-before-entry',save=3922)
    before=(full/'current.state',3922,full)
    after=run('author-after-entry',load=before,save=3923)
    active=run('author-playing-voice',load=before,save=3934)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    allhashes=hashes(full);allpcm=pcm(full);entries=list(csv.DictReader((full/'entries.csv').open()))
    checks['three_full_reference_entries']=len(entries)==3 and all(r['emitted']=='1' for r in entries)
    states=[(3922,full),(3923,after),(3934,active)]
    for field,origin in states:
        state=origin/'current.state';identity=digest(state)
        for mode in ('aot','lle'):
            name=f'{field}-{mode}';folder=run(name,load=(state,field,origin),mode=mode)
            expected=[r for r in allhashes if int(r[0])>field]
            checks[name+'_every_guest_field_and_first_loaded_field_exact']=len(expected)==4600-field and hashes(folder)==expected
            tail=pcm(folder);checks[name+'_whole_playing_audio_suffix_exact']=bool(tail) and allpcm[-len(tail):]==tail
            actual=list(csv.DictReader((folder/'entries.csv').open())) if (folder/'entries.csv').exists() else []
            checks[name+'_no_duplicate_or_lost_entry']=actual==[r for r in entries if int(r['field'])>field]
            checks[name+'_final_scene_exact']=digest(folder/'scene.json')==digest(full/'scene.json')
            checks[name+'_final_client_exact']=digest(folder/'window.png')==digest(full/'window.png')
        checks[str(field)+'_checkpoint_unchanged']=digest(state)==identity
    paths=[Path(__file__),bp,source,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,checkpoint_fields=[f for f,_ in states],
                current_build_only=True,legacy_compatibility_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
