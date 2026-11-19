"""Bind ordinary hyena starting health and first successful hit on each difficulty.

This verifies six bounded encounters, not complete AI/attack-region equivalence.
Native and MD routes retain their distinct camera, scene and scheduling history.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound
from verify_windows import hashes


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reuse-windows',type=Path,help='Reuse the bound unchanged Windows runs after correcting only the opcode expectation')
    args=ap.parse_args()
    base=ROOT/'build/pride-hyena-hits';out=base/'verification2';out.mkdir(exist_ok=False)
    reports={s:bound(base/s/'report.json') for s in ('snes','md')}
    paths=[Path(__file__),ROOT/'tools/summarize_pride_practice.py',
           *[base/s/'report.json' for s in reports]]
    checks={};observations={}
    snes=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    md=(ROOT/'Lion King, The (World).md').read_bytes()
    # Both original action initializers subtract one from actor+2A.
    checks['original_native_hit_decrement']=snes[0x14769:0x14771]==bytes.fromhex('a02a00b1003a9100')
    checks['original_md_hit_decrement']=md[0x19b93e:0x19b944]==bytes.fromhex('04690001002a')
    exe=ROOT/'build/pride-arena-work/tlk_pride_player.exe';paths.append(exe)
    if args.reuse_windows:
        previous=bound(args.reuse_windows)
        assert previous['result']=='FAILED_OPCODE_EXPECTATION' and previous['binary_sha256']==digest(exe)
        assert previous['capture_reports_sha256']=={s:digest(base/s/'report.json') for s in reports}
        paths.append(args.reuse_windows.resolve())
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for name,maximum in [('easy',1),('normal',2),('hard',3)]:
        observations[name]={}
        for source in ('snes','md'):
            case=reports[source]['cases'][name]
            rows=json.loads((base/source/name/'frames.json').read_text())
            first,hit=case['changes'][:2]
            checks[name+'_'+source+'_starting_health']=first['candidate_health']==maximum
            checks[name+'_'+source+'_first_hit']=hit['candidate_health']==maximum-1
            expected=(0xc147f7 if maximum==1 else 0xc1470f) if source=='snes' else (0x19b9e0 if maximum==1 else 0x19b904)
            checks[name+'_'+source+'_reaction']=hit['action']==expected
            checks[name+'_'+source+'_scene']=first['level']==hit['level']==(0 if source=='snes' else 1)
            checks[name+'_'+source+'_actor_ownership']=len({r['actor'] for r in rows})==1
            observations[name][source]=dict(actor=hex(first['actor']),health=maximum,
                first_sample=first['field'],hit_sample=hit['field'],reaction=hex(hit['action']))
        hit=reports['snes']['cases'][name]['changes'][1]['field']
        folder=(args.reuse_windows.parent if args.reuse_windows else out)/name
        if not args.reuse_windows:folder.mkdir()
        cfg=folder/'host.ini'
        if not args.reuse_windows:cfg.write_text('opengl = 0\nscale = 2\n')
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',base/'snes'/name/'resources.ini',
             '--config',cfg,'--input-polled',base/'snes'/name/'ordinary.polled.tape','--frames',hit,
             '--hash-at',str(hit),'--no-pace','--no-audio','--no-record',
             '--dump-scene',folder/'scene.json','--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        if not args.reuse_windows:
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
        checks[name+'_actual_player_wram']=hashes(folder/'run.log')['wram_sha256']==digest(base/'snes'/name/f'hl_wram_{hit}.bin')
        scene=json.loads((folder/'scene.json').read_text())
        checks[name+'_actual_arena_scene']=scene['level']==0 and scene['latched_gameplay']['descriptor']==0x80d
    assert all(checks.values()),checks
    result=dict(result='BOUNDED_HYENA_HEALTH_AND_FIRST_HIT_MATCH',scope=__doc__,checks=checks,observations=observations,
        full_difficulty_or_enemy_equivalence=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks',flush=True)


if __name__=='__main__':main()
