"""Basic current checkpoints around the first early lizard cue, without migrations."""
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
    base=ROOT/'build/pride-lizard-voice74';bp=base/'build-report.json';bound(bp)
    source=base/'voice-fight/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'voice-resume';out.mkdir();checks={};commands={};end=1300
    template=prior['commands']['md-aot'].copy();template[0]=str(base/'player.exe');template[template.index('--frames')+1]=str(end)
    profile=Path(template[template.index('--resource-profile')+1]).read_text()
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name,load=None,save=None,mode='aot'):
        folder=out/name;folder.mkdir();cmd=template.copy();(folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_text(profile)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if load:
            field,origin=load;cmd+=['--load',str(origin/'current.state')]
            row=next(json.loads(line) for line in (origin/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==field)
            origin_cmd=commands[origin.name];origin_tape=Path(origin_cmd[origin_cmd.index('--input-polled')+1])
            remaining=folder/'remaining.polled.tape';remaining.write_bytes(origin_tape.read_bytes()[row['poll_index']*2:]);cmd[cmd.index('--input-polled')+1]=str(remaining)
        if save:cmd+=['--save-at',str(save),str(folder/'current.state')]
        if mode=='lle':cmd+=['--lle']
        commands[name]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_LIZARD_ATTACK_TRACE=str(folder/'entries.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;print(name,rc,flush=True);return folder
    full=run('author-before-entry',save=1085)
    after=run('author-after-entry',load=(1085,full),save=1086)
    active=run('author-native-cue-boundary',load=(1085,full),save=1105)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    allhashes=hashes(full);allpcm=pcm(full);entries=list(csv.DictReader((full/'entries.csv').open()))
    checks['both_natural_early_cues_in_reference']=len(entries)==2 and all(r['emitted']=='1' for r in entries)
    fight=source.parent/'md-aot';checks['reference_all1300_guest_fields_match_full_win']=len(allhashes)==end and allhashes==[r for r in hashes(fight) if int(r[0])<=end]
    checks['reference_pcm_is_full_win_prefix']=bool(allpcm) and pcm(fight)[:len(allpcm)]==allpcm
    for label,folder in (('after',after),('native-cue',active)):
        checks[label+'_author_tail_guest_exact']=hashes(folder)==[r for r in allhashes if int(r[0])>1085]
        tail=pcm(folder);checks[label+'_author_tail_pcm_exact']=bool(tail) and allpcm[-len(tail):]==tail
    for field,origin in ((1085,full),(1086,after),(1105,active)):
        identity=digest(origin/'current.state')
        for mode in ('aot','lle'):
            name=f'{field}-{mode}';folder=run(name,load=(field,origin),mode=mode)
            expected=[r for r in allhashes if int(r[0])>field]
            checks[name+'_all_remaining_guest_and_first_loaded_fields_exact']=len(expected)==end-field and hashes(folder)==expected
            tail=pcm(folder);checks[name+'_playing_audio_suffix_exact']=bool(tail) and allpcm[-len(tail):]==tail
            resumed=list(csv.DictReader((folder/'entries.csv').open())) if (folder/'entries.csv').exists() else []
            checks[name+'_no_duplicate_or_lost_cue']=resumed==[r for r in entries if int(r['field'])>field]
            for file in ('scene.json','window.png'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(full/file)
        checks[str(field)+'_checkpoint_unchanged']=digest(origin/'current.state')==identity
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,end_field=end,checkpoint_fields=[1085,1086,1105],
                current_build_only=True,legacy_compatibility_claimed=False,full_route_completion_qualified_separately=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
