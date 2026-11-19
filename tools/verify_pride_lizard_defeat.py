"""Verify the original MD-only lizard defeat cue through ordinary input and saves."""
import csv
import hashlib
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes
from verify_pride_audio_state import wav_data


def main():
    out=ROOT/'build/pride-lizard-defeat';out.mkdir(exist_ok=True)
    original=json.loads((ROOT/'build/lizard-defeat-original/native.json').read_text())
    assert [e['frame'] for e in original['entries']]==[1430,1621]
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    native=out/'prepare.ini';native.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';ready=out/'ready.state'
    command=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--resource-profile',str(native),'--frames','1400','--input-polled',str(tape),
             '--save-at','1400',str(ready)]
    with (out/'prepare.log').open('wb') as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    used=int(re.search(r'tape_words_used=(\d+)',(out/'prepare.log').read_text()).group(1))
    after=out/'after.polled.tape';after.write_bytes(tape.read_bytes()[used*2:])
    profiles={}
    common='schema = 1\ngame = snes\naudio.music.pride_lands = md\naudio.effects.simba.bounce = md\n'
    for name,extra in {'native':'','md':'audio.effects.world.defeat_puff = md\n',
                       'sibling':'audio.effects.world.hyena_taunt = md\n'}.items():
        path=out/(name+'.ini');path.write_text(common+extra);profiles[name]=path
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
          '--no-pace','--no-audio','--no-record']
    def run(name,source='md',state=ready,inputs=after,end=1700,extra=()):
        stem=out/name;env=os.environ.copy()
        env.update(TLK_LIZARD_DEFEAT_TRACE=str(stem)+'-triggers.csv',
                   TLK_MD_SOUND_COMMANDS=str(stem)+'-commands.csv',TLK_AUDIO_STEMS=str(stem)+'-stems.csv')
        cmd=base+['--resource-profile',str(profiles[source]),'--load',str(state),'--input-polled',str(inputs),
                  '--frames',str(end),'--wav',str(stem)+'.wav',*map(str,extra)]
        log=stem.with_suffix('.log')
        with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        assert 'Saved resource profile loaded' in log.read_text(),(name,'Source rejected')
        trigger_file=out/(name+'-triggers.csv')
        triggers=list(csv.DictReader(trigger_file.open())) if trigger_file.exists() else []
        commands=list(csv.DictReader(open(str(stem)+'-commands.csv')))
        cues=[r for r in commands if r['selector']=='2' and r['value']=='165']
        return {'hashes':hashes(log),'triggers':triggers,'cues':cues,'wav':wav_data(stem.with_suffix('.wav'))}
    results={}
    for mode,source,extra in [('native','native',()),('md-aot','md',()),('md-lle','md',('--lle',)),('sibling','sibling',())]:
        results[mode]=run(mode,source,extra=extra)
        row=results[mode];assert len(row['triggers'])==2 and all(r['timer']=='30' for r in row['triggers'])
        assert len(row['cues'])==(2 if source=='md' else 0)
        assert all(r['emitted']==('1' if source=='md' else '0') for r in row['triggers'])
    assert len({tuple(r['hashes'].items()) for r in results.values()})==1,'Sound changed guest state'
    assert results['md-aot']['wav']==results['md-lle']['wav'],'AOT/LLE audio differs'
    assert results['native']['wav']==results['sibling']['wav'],'Sibling selection changed this cue'
    left,right=results['native']['wav'],results['md-aot']['wav']
    first=next(i for i,(a,b) in enumerate(zip(left,right)) if a!=b)
    before=int((1432-1400-1)*48000*357366/21477272)*4
    assert before<=first<before+3*800*4,('Audible change outside the original timer update',first,before)
    print('Two natural defeat cues, audible MD-only addition, independent sibling and AOT/LLE PASS',flush=True)
    saves=[]
    for frame in (1430,1431,1432,1434):
        state=out/f'{frame}.state'
        run(str(frame)+'-save',end=frame,extra=['--save-at',frame,state])
        used=int(re.search(r'tape_words_used=(\d+)',(out/(str(frame)+'-save.log')).read_text()).group(1))
        suffix=out/f'{frame}.polled.tape';suffix.write_bytes(after.read_bytes()[used*2:])
        loaded=run(str(frame)+'-loaded',state=state,inputs=suffix)
        assert loaded['hashes']==results['md-aot']['hashes']
        assert results['md-aot']['wav'][-len(loaded['wav']):]==loaded['wav'],(frame,'Playing continuation differs')
        assert len(loaded['cues'])==(2 if frame<1432 else 1),(frame,'Repeated or missing timer cue')
        saves.append(frame)
    # Isolated sound-disable fixture changes only the original native Options
    # FX word, preserving the ordinary input route. It is not completion proof.
    env=os.environ.copy();env.update(TLK_WRAM_DUMP='1400',TLK_WRAM_DIR=str(out))
    with (out/'fx-prepare.log').open('wb') as log:subprocess.run(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    ram=(out/'hl_wram_1400.bin').read_bytes();raw=bytearray(ready.read_bytes());at=raw.find(ram)
    assert at>=0 and raw.find(ram,at+1)<0
    struct.pack_into('<H',raw,at+0x1ff96,0)
    muted=out/'fx-disabled.state';muted.write_bytes(raw)
    disabled=run('fx-disabled',state=muted)
    assert len(disabled['triggers'])==2 and not disabled['cues']
    assert all(r['emitted']=='0' for r in disabled['triggers'])
    report={'result':'PASS','scope':__doc__,'ordinary_defeats':2,'native_has_no_separate_cue':True,
            'original_md_selector':2,'original_md_value':165,'original_timer_before_decrement':30,
            'source_id':'audio.effects.world.defeat_puff','new_audio_first_difference_byte':first,
            'guest_hashes_all_sources_and_modes_equal':True,'sibling_audio_unchanged':True,'md_aot_lle_wav_equal':True,
            'mid_action_save_points':saves,'all_resumed_wav_bytes_exact':True,'sound_disabled_fixture_emits_nothing':True,
            'md_wav_sha256':hashlib.sha256(right).hexdigest()}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Four timer/playing-tail saves and sound-disable guard PASS',flush=True)


if __name__=='__main__':main()
