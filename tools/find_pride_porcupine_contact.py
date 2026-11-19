"""Find ordinary-input hurt candidates; enemy attribution is a separate check."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-contact-search';out.mkdir()
    source=ROOT/'build/pride-porcupine38/contact-seed/report.json';seed=bound(source)
    assert seed['checks']['exit']
    origin=source.parent
    state=origin/'saved.state'
    tree=[json.loads(line) for line in (origin/'tree.jsonl').read_text().splitlines()]
    assert tree[-1]['field']==1400
    used=tree[-1]['poll_index']
    prefix=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[:used*2]
    patterns={'neutral':[0]*200}
    for direction,pad in [('left',0x200),('right',0x100)]:
        for duration in (4,8,16,32):patterns[direction+str(duration)]=[pad]*duration+[0]*(200-duration)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    commands={};cases={}
    for label,pads in patterns.items():
        folder=out/label;folder.mkdir()
        tape=folder/'tail.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        cmd=seed['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--input-polled',tape),('--frames',1600),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--load',str(state)];commands[label]=cmd
        env=dict(clean,TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert run.returncode==0,(label,run.returncode)
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        hits=[dict(field=b['field'],before=a['health'],after=b['health']) for a,b in zip(rows,rows[1:]) if b['health']<a['health']]
        events=list(csv.DictReader((folder/'events.csv').open()))
        cases[label]=dict(health_drops=hits,final_health=rows[-1]['health'],
                         hurt_events=[r for r in events if r['event']=='0014'],enemy_attribution_proven=False)
        if hits:
            full=folder/'poweron.polled.tape';full.write_bytes(prefix+tape.read_bytes())
            cases[label]['poweron_tape']=full.relative_to(ROOT).as_posix()
        print(label,cases[label],flush=True)
    paths=[Path(__file__),source,state,ROOT/'engine/tapes/allbugsF.read.tape']
    report=dict(result='HURT_CANDIDATES' if any(c['health_drops'] for c in cases.values()) else 'NO_HURT_FOUND',cases=cases,
                commands=commands,anchor_poll_offset=used,ordinary_controls_only=True,guest_rom_or_rng_edits=False,
                enemy_attribution_proven=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
