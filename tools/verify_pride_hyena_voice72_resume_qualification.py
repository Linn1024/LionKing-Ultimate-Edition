"""Correct remaining-input offsets for current checkpoints authored after a load."""
import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-hyena-voice72';source=base/'voice-resume/report.json';prior=bound(source)
    assert prior['result']=='FAIL'
    out=base/'voice-resume-qualification';out.mkdir();checks={};commands={};observations={}
    origin=source.parent;full=origin/'author-before-entry'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:return stream.readframes(stream.getnframes())
    allhashes=hashes(full);allpcm=pcm(full);entries=list(csv.DictReader((full/'entries.csv').open()))
    checks['before_entry_both_mode_resumes_already_exact']=all(v for k,v in prior['checks'].items() if k.startswith('3922-'))
    checks['all_author_and_resume_processes_exit']=all(v for k,v in prior['checks'].items() if k.endswith('_exit'))
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    for field,label in ((3923,'author-after-entry'),(3934,'author-playing-voice')):
        author=origin/label;author_cmd=prior['commands'][label]
        checks[label+'_author_tail_guest_exact']=hashes(author)==[r for r in allhashes if int(r[0])>3922]
        apcm=pcm(author);checks[label+'_author_audio_tail_exact']=bool(apcm) and allpcm[-len(apcm):]==apcm
        actual_tape=Path(author_cmd[author_cmd.index('--input-polled')+1])
        row=next(json.loads(line) for line in (author/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']==field)
        used=row['poll_index'];remaining=actual_tape.read_bytes()[used*2:]
        observations[str(field)]=dict(author_input=str(actual_tape.relative_to(ROOT)),process_relative_polls=used,remaining_bytes=len(remaining))
        for mode in ('aot','lle'):
            name=f'{field}-{mode}';folder=out/name;folder.mkdir();cmd=prior['commands'][name].copy()
            for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
                shutil.copy2(Path(cmd[cmd.index(flag)+1]),folder/file);cmd[cmd.index(flag)+1]=str(folder/file)
            tail=folder/'remaining.polled.tape';tail.write_bytes(remaining);cmd[cmd.index('--input-polled')+1]=str(tail)
            for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
            commands[name]=cmd
            env=dict(clean,TLK_HYENA_VOICE_TRACE=str(folder/'entries.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
            checks[name+'_exit']=rc==0
            expected=[r for r in allhashes if int(r[0])>field]
            checks[name+'_every_guest_field_and_first_loaded_field_exact']=len(expected)==4600-field and hashes(folder)==expected
            actual=pcm(folder);checks[name+'_playing_audio_suffix_exact']=bool(actual) and allpcm[-len(actual):]==actual
            resumed=list(csv.DictReader((folder/'entries.csv').open())) if (folder/'entries.csv').exists() else []
            checks[name+'_no_duplicate_or_lost_entry']=resumed==[r for r in entries if int(r['field'])>field]
            for file in ('window.png','scene.json'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(full/file)
            print(name,rc,flush=True)
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                original_failed_report_retained=True,checkpoint_bytes_or_runtime_not_changed=True,current_build_only=True,
                correction='A loaded author consumes its own remaining tape; its poll_index cannot index the original full power-on tape.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
