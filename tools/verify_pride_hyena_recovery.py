"""Check bounded hurt recovery and repeated-hit victory with actual Windows views."""
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
    base=ROOT/'build/pride-hyena-recovery';out=base/'verification2';out.mkdir(exist_ok=False)
    reports={s:bound(base/s/'report.json') for s in ('snes','md')}
    catalog=ROOT/'tools/pride_npc_pairs.json'
    pairs={int(r['snes'],16):int(r['md'],16) for r in json.loads(catalog.read_text())['pairs'] if r['role']=='hyena'}
    checks={};observations={}
    exe=ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    paths=[Path(__file__),catalog,exe,*[base/s/'report.json' for s in reports]]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for name,maximum in [('normal',2),('hard',3)]:
        data={s:json.loads((base/s/name/'frames.json').read_text()) for s in reports}
        starts={s:next(i for i,r in enumerate(data[s]) if r['action']==(0xc1470f if s=='snes' else 0x19b904)) for s in reports}
        native=data['snes'][starts['snes']:starts['snes']+64]
        md=data['md'][starts['md']:starts['md']+64]
        checks[name+'_first_33_hurt_actions']=all(a['action']==0xc1470f and b['action']==0x19b904 for a,b in zip(native[:33],md[:33]))
        checks[name+'_first_33_pose_pairs']=all(pairs.get(a['pose'])==b['pose'] for a,b in zip(native[:33],md[:33]))
        checks[name+'_wait_entry_at_33']=native[33]['action']==0xc13c83 and md[33]['action']==0x19adc0
        checks[name+'_first_64_motion_and_parameters']=all(all(a[k]==b[k] for k in ('x','y','health','timer','cycle','tag','facing')) for a,b in zip(native,md))
        observations[name]={}
        for source in reports:
            rows=data[source];changes=reports[source]['cases'][name]['changes']
            checks[name+'_'+source+'_all_hit_losses']=[r['health'] for r in changes]==list(range(maximum,-1,-1))
            checks[name+'_'+source+'_owned_death']=rows[-1]['health']==0 and rows[-1]['action']==(0xc147f7 if source=='snes' else 0x19b9e0)
            checks[name+'_'+source+'_no_life_loss']=len({r['lives'] for r in rows})==1 and rows[-1]['player_health']>0
            observations[name][source]=dict(health_loss_fields=[r['field'] for r in changes[1:]],
                final_player_health=rows[-1]['player_health'],final_field=rows[-1]['field'])
        plan=ROOT/('build/pride-hyena-normal-repeat-plan' if name=='normal' else 'build/pride-native-hyena-hard-repeat-plan')
        anchor=plan/'anchor/end.state';anchor_log=plan/'anchor'/('game.log' if name=='normal' else 'run.log')
        used=int(re.search(r'tape_words_used=(\d+)',anchor_log.read_text()).group(1))
        tape=plan/('best.polled.tape' if name=='normal' else 'selected.polled.tape')
        # Rollback blobs are build-specific. Author the Windows continuation in
        # this same public player; the older headless checkpoint is not loadable.
        ready=out/(name+'-ready');ready.mkdir();cfg=ready/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
        owned=ready/'4000.state'
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',ROOT/f'build/pride-hyena-hits/snes/{name}/resources.ini',
             '--config',cfg,'--input-polled',tape,'--frames',4000,'--save-at',4000,owned,'--hash-at','4000',
             '--no-pace','--no-audio','--no-record']
        with (ready/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        checks[name+'_actual_4000_anchor']=hashes(ready/'run.log')['wram_sha256']==digest(base/'snes'/name/'hl_wram_4000.bin')
        used=int(re.search(r'tape_words_used=(\d+)',(ready/'run.log').read_text()).group(1))
        suffix=out/(name+'.polled.tape');suffix.write_bytes(tape.read_bytes()[used*2:])
        paths.extend([anchor,anchor_log,tape])
        for label,end in [('wait-entry',native[33]['field']),('victory',data['snes'][-1]['field'])]:
            folder=out/(name+'-'+label);folder.mkdir();cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',ROOT/f'build/pride-hyena-hits/snes/{name}/resources.ini',
                '--config',cfg,'--load',owned,'--input-polled',suffix,'--frames',end,'--hash-at',str(end),
                '--no-pace','--no-audio','--no-record','--dump-scene',folder/'scene.json',
                '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
            checks[name+'_'+label+'_actual_guest']=hashes(folder/'run.log')['wram_sha256']==digest(base/'snes'/name/f'hl_wram_{end}.bin')
            scene=json.loads((folder/'scene.json').read_text())
            checks[name+'_'+label+'_actual_arena']=scene['level']==0 and scene['latched_gameplay']['descriptor']==0x80d
    assert all(checks.values()),checks
    result=dict(result='BOUNDED_HURT_RECOVERY_AND_REPEATED_HITS_VERIFIED',checks=checks,observations=observations,
        scope=__doc__,whole_ai_or_attack_region_equivalence=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks',flush=True)


if __name__=='__main__':main()
