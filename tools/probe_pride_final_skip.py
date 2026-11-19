"""Compare an excluded final-life display bypass with the untouched player.

This tests feasibility and return context, not full original MD final fidelity.
Only the separate probe executable redirects guest execution when requested.
"""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_bounce_owner_preview_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    out=ROOT/'build/pride-final-skip';out.mkdir()
    probe=ROOT/'build/pride-bounce-owner-work/player/final-skip-probe'
    bp=probe/'build-report.json';assert digest(probe/'player.exe')==bound(bp)['binary_sha256']
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    tape=ROOT/'build/pride-game-over-music/hard.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    runs={};commands={};checks={}
    for label,exe,skip in (('public',public,False),('control',probe/'player.exe',False),('skip',probe/'player.exe',True)):
        folder=out/label;folder.mkdir();env=dict(clean)
        if label!='public':env.update(TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP=str(int(skip)))
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profile,'--input',tape,'--lle','--frames',3000,
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,3001))),
            '--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds',100]))
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        rows=re.findall(PATTERN,(folder/'run.log').read_text());checks[label+'/all_3000_samples']=len(rows)==3000
        points=list(csv.DictReader((folder/'points.csv').open())) if label!='public' else []
        runs[label]=dict(samples=rows,points=points)
        print(label,'complete',points,flush=True)
    checks['read_only_control_all_guest_fields']=runs['public']['samples']==runs['control']['samples']
    checks['read_only_control_whole_pcm']=wav_data(out/'public/audio.wav')==wav_data(out/'control/audio.wav')
    checks['read_only_control_real_client']=pixels(out/'public/window.png')==pixels(out/'control/window.png')
    control=runs['control']['points'];skip=runs['skip']['points']
    final=next((r for r in control if r['pc']=='c089b9' and r['spares']=='0'),None)
    over=next((r for r in skip if r['pc']=='c08b22'),None)
    checks['natural_final_death_observed']=bool(final)
    checks['experimental_game_over_entry_observed']=bool(over)
    if final:
        count=int(final['field'])-1
        checks['experiment_every_prefatal_guest_field_preserved']=runs['skip']['samples'][:count]==runs['public']['samples'][:count]
    paths=[Path(__file__),ROOT/'tools/pride_final_skip_probe.c',bp,public,tape,ROOT/'build/pride-game-over-music/input-provenance.json']
    report=dict(result='FEASIBILITY_ONLY' if all(checks.values()) else 'FAIL',checks=checks,runs=runs,commands=commands,
        interpreter_only_experiment=True,experimental_guest_execution_redirect=True,
        builder_read_only_flag_applies_only_to_control_mode=True,
        compiled_redirect_supported=False,original_final_scene_timing_proven=False,
        final_death_gameplay_resource_enabled=False,production_changed=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks; failures',[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
