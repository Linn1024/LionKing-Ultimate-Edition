"""Use the existing RNG-on wide route, preserving its gameplay inputs exactly."""
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-restart-difficulty25'
    source=base/'completion2/report.json';prior=bound(source)
    historical=ROOT/'build/pride-rng-player2/completion-reference-unpaused2/report.json'
    wide=bound(historical);template=wide['commands']['320/aot']
    original=Path(template[template.index('--input-polled')+1])
    corrected=ROOT/'build/pride-restart-prefix-spaced99/report.json';prefix=bound(corrected)
    out=base/'wide-completion';out.mkdir();checks={};commands={};observations={}
    old=original.read_bytes()
    adapted=Path(prefix['command'][prefix['command'].index('--input-polled')+1]).read_bytes()
    native=(ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape').read_bytes()
    checks['same_original_menu_prefix']=old[:638*2]==native[:638*2]
    tape=out/'ordinary.polled.tape';tape.write_bytes(adapted[:737*2]+old[638*2:])
    checks['wide_gameplay_suffix_exact']=tape.read_bytes()[737*2:]==old[638*2:]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for lle in (False,True):
        label='lle' if lle else 'aot';folder=out/label;folder.mkdir()
        cmd=prior['commands']['320-md'].copy()
        for flag,value in [('--input-polled',tape),('--frames',6000),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if lle:cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl')),
                                  stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[label]=cmd;checks[label+'_exit']=result.returncode==0
        scene=json.loads((folder/'scene.json').read_text());checks[label+'_next_level']=scene['level']==1
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        first=next((r for r in rows if r['descriptor']==0xc00387 and r['level']==0),None)
        checks[label+'_easy']=first is not None and first['difficulty']==0
        observations[label]=dict(first_pride=first,final_level=scene['level'])
        print(label,'level',scene['level'],flush=True)
    checks['guest_equal']=hashes(out/'aot/run.log')==hashes(out/'lle/run.log')
    checks['client_equal']=pixels(out/'aot/window.png')==pixels(out/'lle/window.png')
    checks['full_pcm_equal']=pcm(out/'aot/audio.wav')==pcm(out/'lle/audio.wav')
    paths=[Path(__file__),base/'build-report.json',source,historical,original,corrected]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                ordinary_inputs=True,guest_or_rom_edits=False,full_first_level_fidelity_complete=False,
                recording_credit='Inherited ShgofcTAS All Bugs Final / MD controller authoring; CC BY2.0; see docs/pride-rng-player.md and original controller provenance.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
