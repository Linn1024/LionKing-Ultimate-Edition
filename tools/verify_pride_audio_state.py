"""Verify exact mixed-audio continuation, legacy fallback and invalid records."""
import csv
import hashlib
import json
import os
import struct
import subprocess
import wave
from audit_scenes import ROOT
from verify_windows import hashes


def audio_offset(raw):
    at=36+struct.unpack_from('<Q',raw,24)[0]
    return at+4+struct.unpack_from('<I',raw,at)[0]+4


def seal(raw):
    """Recompute envelope checksums for semantic rejection/rollback fixtures."""
    at=audio_offset(raw)
    nested,native=struct.unpack_from('<II',raw,at+40)
    if nested and native<=len(raw)-at-128:
        md=at+128+native
        raw[md+88:md+120]=bytes(32)
        raw[md+88:md+120]=hashlib.sha256(raw[md:md+nested]).digest()
    raw[at+80:at+112]=bytes(32)
    raw[at+80:at+112]=hashlib.sha256(raw[at:]).digest()
    return raw


def wav_data(path):
    with wave.open(str(path),'rb') as wav:
        assert wav.getnchannels()==2 and wav.getframerate()==48000
        return wav.readframes(wav.getnframes())


def main():
    out=ROOT/'build/pride-audio-state';out.mkdir(exist_ok=True)
    source=ROOT/'build/pride-hyena-taunt'
    ready=source/'ready.state'
    zero=out/'zero.tape';zero.write_bytes(bytes(4300*2))
    pause=bytearray(zero.read_bytes())
    for frame in (*range(4029,4032),*range(4050,4053)):
        struct.pack_into('<H',pause,frame*2,0x1000)
    pause_tape=out/'pause.tape';pause_tape.write_bytes(pause)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
          '--no-pace','--no-audio','--no-record']
    profiles={}
    for name,extra in {
        'native':'','taunt':'audio.effects.world.hyena_taunt = md\n',
        'music':'audio.music.pride_lands = md\n',
        'mixed':'audio.music.pride_lands = md\naudio.effects.world.hyena_taunt = md\n',
        'media':'audio.music.pride_lands = md\naudio.effects.world.hyena_taunt = md\ngraphics.scenery = md\ndisplay.viewport = md\n',
    }.items():
        path=out/(name+'.ini');path.write_text('schema = 1\ngame = snes\n'+extra);profiles[name]=path

    def run(name,profile,state,extra=(),inputs=zero,expect=0):
        stem=out/name;env=os.environ.copy();env['TLK_AUDIO_STEMS']=str(stem)+'.csv'
        command=base+['--resource-profile',str(profiles[profile]),'--load',str(state),
                      '--input',str(inputs),'--frames','4070','--wav',str(stem)+'.wav',*map(str,extra)]
        log=stem.with_suffix('.log')
        with log.open('wb') as stream:
            result=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
        assert result.returncode==expect,(name,result.returncode,log.read_text()[-1200:])
        return stem

    results={}
    for case,profile,inputs,save_at in (
            ('native','native',zero,4030),('taunt','taunt',zero,4030),
            ('music','music',zero,4030),('mixed','mixed',zero,4030),
            ('media','media',zero,4030),('paused','mixed',pause_tape,4040)):
        state=out/(case+'.state')
        full=run(case+'-full',profile,ready,['--save-at',save_at,state],inputs)
        raw=state.read_bytes();assert struct.unpack_from('<I',raw,8)[0]==4
        loaded=run(case+'-loaded',profile,state,inputs=inputs)
        expected,actual=wav_data(full.with_suffix('.wav')),wav_data(loaded.with_suffix('.wav'))
        assert actual and expected[-len(actual):]==actual,(case,'Mixed continuation WAV differs')
        assert hashes(full.with_suffix('.log'))==hashes(loaded.with_suffix('.log')),(case,'Guest continuation differs')
        # A timed load consumes the current field before rewinding; audio after
        # that boundary must repeat exactly, with no extra driver commands.
        timed=run(case+'-timed',profile,ready,['--load-at','4055',state],inputs)
        assert wav_data(timed.with_suffix('.wav'))[-len(actual):]==actual,(case,'Timed load WAV differs')
        assert hashes(timed.with_suffix('.log'))==hashes(full.with_suffix('.log'))
        results[case]={'continuation_bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()}
        print(case,'new-process/timed mixed WAV and guest continuation exact PASS',flush=True)

    lle_state=out/'mixed-lle.state'
    lle=run('mixed-lle-full','mixed',ready,['--lle','--save-at','4030',lle_state])
    loaded=run('mixed-lle-loaded','mixed',lle_state,['--lle'])
    assert wav_data(lle.with_suffix('.wav'))==wav_data(out/'mixed-full.wav'),'Continuous AOT/LLE audio differs'
    assert wav_data(loaded.with_suffix('.wav'))==wav_data(out/'mixed-loaded.wav'),'Loaded AOT/LLE audio differs'
    assert hashes(lle.with_suffix('.log'))==hashes(loaded.with_suffix('.log'))==hashes(out/'mixed-full.log')

    # Save actually paused inside the voice, then ordinary Start unpauses it.
    env=os.environ.copy();env.update(TLK_WRAM_DUMP='4041',TLK_WRAM_DIR=str(out))
    with (out/'pause-check.log').open('wb') as log:
        subprocess.run([str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                        '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profiles['mixed']),
                        '--load',str(out/'paused.state'),'--frames','4041'],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    ram=(out/'hl_wram_4041.bin').read_bytes();assert struct.unpack_from('<H',ram,0xa89)[0]
    changed=run('changed-art','media',out/'mixed.state')
    assert wav_data(changed.with_suffix('.wav'))==wav_data(out/'mixed-loaded.wav')
    changed=run('changed-audio','native',out/'taunt.state')
    assert not list(csv.DictReader(changed.with_suffix('.csv').open())), 'Foreign MD voice leaked after source change'
    rate_config=out/'rate44100.ini';rate_config.write_text('opengl = 1\nscale = 2\naudio_rate = 44100\n')
    changed=run('changed-rate','taunt',out/'taunt.state',['--config',rate_config])
    assert not list(csv.DictReader(changed.with_suffix('.csv').open())), 'Incompatible-rate tail was restored'
    with wave.open(str(changed.with_suffix('.wav')),'rb') as wav:assert wav.getframerate()==44100

    # Real v1/v2/v3 layouts omit the newer sections, rather than just changing
    # a version number over a v4 file. All remain loadable with native gameplay.
    raw=(out/'mixed.state').read_bytes();blob_end=36+struct.unpack_from('<Q',raw,24)[0]
    view_end=audio_offset(raw)-4
    for version in (1,2,3):
        if version==1:
            old=bytearray(raw[:32]+raw[36:blob_end])
        else:old=bytearray(raw[:blob_end if version==2 else view_end])
        struct.pack_into('<I',old,8,version)
        path=out/f'legacy-{version}.state';path.write_bytes(old)
        run('legacy-'+str(version),'mixed',path)

    original=bytearray((out/'mixed.state').read_bytes());at=audio_offset(original)
    cases={}
    for name,offset,value,fmt in (
            ('schema',at+8,99,'<I'),('fraction',at+32,float('nan'),'<d'),
            ('native-length',at+44,0xffffffff,'<I'),('tail-count',at+16,121,'<I')):
        raw=original.copy();struct.pack_into(fmt,raw,offset,value);cases[name]=seal(raw)
    raw=original.copy();raw[-1]^=1;cases['checksum']=raw
    cases['truncated']=original[:-1];cases['trailing']=original+b'x'
    raw=original.copy();native=struct.unpack_from('<I',raw,at+44)[0];md=at+128+native
    core=md+120+32768*4+struct.unpack_from('<I',raw,md+48)[0]*8
    raw[core]^=1;cases['backend-rejection']=seal(raw)
    for name,raw in cases.items():
        path=out/('invalid-'+name+'.state');path.write_bytes(raw)
        run('reject-'+name,'mixed',path,expect=8)
        assert path.read_bytes()==raw
    report={'result':'PASS','scope':__doc__,'exact_cases':results,'mixed_audio_aot_lle_exact':True,'actual_paused_voice_and_unpause':True,
            'graphics_change_audio_identical':True,'changed_audio_sources_drop_foreign_tail':True,'changed_output_rate_fallback':True,
            'legacy_versions_load':[1,2,3],'invalid_records_rejected':list(cases)}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
