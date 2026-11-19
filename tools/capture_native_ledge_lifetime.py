"""Record every original ledge field and enclosing native audio calls."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-arrival-work/player';observer=base/'contact-audio-lifetime'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=ROOT/'build/native-ledge-lifetime';out.mkdir()
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_NATIVE_CONTACT_AUDIO_TRACE=str(out/'entries.csv'),TLK_AUDIO_EVENTS=str(out/'audio.csv'),
               TLK_NATIVE_CONTACT_LIFETIME=str(out/'lifetime.csv'))
    command=list(map(str,[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
        '--md-rom',out/'missing.md','--config',config,'--resource-profile',profile,'--input-polled',tape,
        '--frames',4500,'--lle','--no-pace','--no-audio','--no-record',
        '--hash-at',','.join(map(str,range(1,4501))),'--dump-window',out/'window.png']))
    with (out/'run.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
    previous=ROOT/'build/native-ledge-audio/allbugs'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:re.findall(pattern,p.read_text())
    assert len(rows(out/'run.log'))==4500 and rows(out/'run.log')==rows(previous/'run.log')
    assert (out/'entries.csv').read_bytes()==(previous/'entries.csv').read_bytes()
    assert (out/'audio.csv').read_bytes()==(previous/'audio.csv').read_bytes()
    life=list(csv.DictReader((out/'lifetime.csv').open()));assert len(life)==4500
    assert [int(r['field']) for r in life]==list(range(1,4501))
    entries=list(csv.DictReader((out/'entries.csv').open()));audio=list(csv.DictReader((out/'audio.csv').open()))
    intervals=[]
    for entry in entries:
        field=int(entry['field']);expected='c33d1f' if entry['entry']=='c351a8' else 'c33f11'
        sequence=[]
        for row in life[field-1:]:
            if row['action']!=expected:break
            sequence.append(row)
        end=int(sequence[-1]['field']) if sequence else field
        related=[r for r in audio if r['actor']==entry['actor'] and field-2<=int(r['frame'])<=end+2]
        intervals.append(dict(entry=entry,expected_ledge_action=expected,initial_post_field=life[field-1],
            consecutive_ledge_fields=len(sequence),last_post_field=sequence[-1] if sequence else None,
            native_audio_in_enclosing_window=related))
    paths=[Path(__file__),bp,tape,previous/'run.log',previous/'entries.csv',previous/'audio.csv']
    report=dict(result='ORIGINAL_LEDGE_LIFETIMES_CAPTURED',intervals=intervals,command=command,
        observer_neutral_all_4500_picture_full_wram_fields=True,
        native_audio_and_entry_traces_unchanged=True,original_guest_or_input_mutations=False,
        all_original_contact_branches_verified=False,production_mapping_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],[(r['entry']['field'],r['expected_ledge_action'],r['consecutive_ledge_fields'],
          len(r['native_audio_in_enclosing_window'])) for r in intervals],flush=True)


if __name__=='__main__':main()
