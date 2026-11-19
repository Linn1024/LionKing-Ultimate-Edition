"""Verify current Normal/Difficult boss victories with independent art/audio."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-hyena-mixtures58';out.mkdir();commands={};checks={};observations={}
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source)
    originalpath=ROOT/'build/pride-hyena-recovery/snes/report.json';original=bound(originalpath)
    template=prior['commands']['aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    catalog=ROOT/'tools/pride_npc_pairs.json';hyenas={int(r['snes'],16) for r in json.loads(catalog.read_text())['pairs'] if r['role']=='hyena'}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    choices={'native':'','art':'graphics.sprites.simba.cub = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.hud = md\n'}
    choices['mixed']=choices['art']+'audio.music.pride_lands = md\naudio.effects.simba.hurt = md\naudio.effects.simba.bounce = md\n'+''.join('audio.effects.world.hyena_'+part+' = md\n' for part in ('hurt','pant','jump','taunt'))
    def run(item):
        difficulty,choice,mode=item;name=f'{difficulty}-{choice}-{mode}';folder=out/name;folder.mkdir();end=original['cases'][difficulty]['final']['field']
        cmd=template.copy();cmd[cmd.index('--frames')+1]=str(end)
        tape=ROOT/('build/pride-hyena-normal-repeat-plan/best.polled.tape' if difficulty=='normal' else 'build/pride-native-hyena-hard-repeat-plan/selected.polled.tape')
        cmd[cmd.index('--input-polled')+1]=str(tape)
        (folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+choices[choice]);(folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        cmd+=['--hash-at',','.join(map(str,range(3950,end+1)))]
        if mode=='lle':cmd+=['--lle']
        elif choice=='mixed':cmd+=['--save-at',str(end-45),str(folder/'current.state')]
        commands[name]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene=json.loads((folder/'scene.json').read_text())
        rows=[json.loads(r) for r in (folder/'tree.jsonl').read_text().splitlines()];last=rows[-1]
        owned=[p for p in scene['pieces'] if p['pose'] in hyenas and p['actor_owner']==p['object'] and p['actor_action']==0xc147f7]
        checks[name+'_exit']=rc==0
        checks[name+'_correct_difficulty']=last['difficulty']==(1 if difficulty=='normal' else 2)
        checks[name+'_alive_in_arena']=scene['level']==0 and scene['latched_gameplay']['descriptor']==0x80d and scene['latched_gameplay']['health']>0
        checks[name+'_owned_boss_death']=bool(owned)
        checks[name+'_no_life_loss']=last['lives']==original['cases'][difficulty]['final']['lives']
        observations[name]=dict(end=end,health=scene['latched_gameplay']['health'],lives=last['lives'],owned_death_pieces=len(owned))
        print(name,rc,observations[name],flush=True)
        return name,folder
    cases=[(difficulty,choice,mode) for difficulty in ('normal','hard') for choice in choices for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool:results=dict(pool.map(run,cases))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for difficulty in ('normal','hard'):
        end=original['cases'][difficulty]['final']['field']
        for choice in choices:
            a=results[f'{difficulty}-{choice}-aot'];b=results[f'{difficulty}-{choice}-lle']
            checks[difficulty+'_'+choice+'_all_fight_guest_fields_mode_parity']=len(hashes(a))==end-3950+1 and hashes(a)==hashes(b)
            for file in ('audio.wav','window.png','scene.json','events.csv'):
                checks[difficulty+'_'+choice+'_'+file+'_mode_parity']=digest(a/file)==digest(b/file)
            if choice!='mixed':
                checks[difficulty+'_'+choice+'_every_original_full_wram_sample']=all(sha==digest(originalpath.parent/difficulty/f'hl_wram_{field}.bin') for field,_,sha in hashes(a))
        a=results[f'{difficulty}-native-aot'];b=results[f'{difficulty}-art-aot'];c=results[f'{difficulty}-mixed-aot']
        checks[difficulty+'_art_keeps_all_guest_fields']=hashes(a)==hashes(b)
        checks[difficulty+'_art_keeps_native_pcm']=digest(a/'audio.wav')==digest(b/'audio.wav')
        checks[difficulty+'_selected_audio_changes_pcm']=digest(b/'audio.wav')!=digest(c/'audio.wav')
    paths=[Path(__file__),source,originalpath,catalog,ROOT/'build/pride-hyena-normal-repeat-plan/best.polled.tape',ROOT/'build/pride-native-hyena-hard-repeat-plan/selected.polled.tape']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                fresh_poweron_inputs_only=True,current_build_save_for_future_window_capture=True,
                original_md_input_history_equivalence_claimed=False,whole_ai_or_arbitrary_contact_equivalence=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
