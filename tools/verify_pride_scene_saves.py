"""Exercise non-Pride native saves with independent Pride behavior enabled."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch3';build_path=base/'build-report.json';build=bound(build_path)
    old_path=ROOT/'build/pride-launch2/build-report.json';old=bound(old_path)
    out=base/'scene-saves';out.mkdir();checks={};commands={};counts=0
    source=ROOT/'profiles/pride-development-preview.ini';text=source.read_text()
    md=out/'md.ini';md.write_text(text);native=out/'native.ini'
    native.write_text(text.replace('gameplay.levels.pride_lands.health_death = md','gameplay.levels.pride_lands.health_death = snes'))
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(folder,exe,profile,level,mode,load=None,save=None):
        folder.mkdir();cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',cfg,'--resource-profile',profile,'--input',tape,'--frames',1800,'--no-pace','--no-audio','--no-record',
             '--hash-at',','.join(map(str,range(1,1801))),'--wav',folder/'audio.wav','--wav-seconds',100,
             '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        cmd+=['--load',load] if load else ['--practice-level',level]
        if mode=='lle':cmd+=['--lle']
        if save:cmd+=['--save-at',1600,save]
        commands[folder.relative_to(out).as_posix()]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert not r.returncode,(folder,r.returncode)
        return re.findall(pattern,(folder/'run.log').read_text())
    for level in (1,10):
        for mode in ('aot','lle'):
            root=out/f'level{level}-{mode}';root.mkdir();state=root/'scene.state'
            cold=root/'cold';rows=run(cold,base/'player.exe',md,level,mode,save=state)
            checks[f'{level}/{mode}/saved']=state.exists()
            assert state.exists(),root
            data=state.read_bytes();before=digest(state)
            checks[f'{level}/{mode}/native_nonpride']=data[:8]==b'TLKSTAT1' and not(int.from_bytes(data[32:36],'little')&0x80000000)
            checks[f'{level}/{mode}/md_source_recorded']=bool(int.from_bytes(data[32:36],'little')&0x20000000)
            for name,profile in (('same-source',md),('other-source',native)):
                resumed=root/name;tail=run(resumed,base/'player.exe',profile,level,mode,load=state)
                audio=wav_data(resumed/'audio.wav');expected=wav_data(cold/'audio.wav')
                checks[f'{level}/{mode}/{name}/all_fields']=tail==[r for r in rows if int(r[0])>1600] and len(tail)==200
                checks[f'{level}/{mode}/{name}/all_pcm']=bool(audio) and audio==expected[-len(audio):]
                checks[f'{level}/{mode}/{name}/guest']=pixels(cold/'guest.png')==pixels(resumed/'guest.png')
                checks[f'{level}/{mode}/{name}/client']=pixels(cold/'window.png')==pixels(resumed/'window.png')
                counts+=len(tail)
            checks[f'{level}/{mode}/input_preserved']=digest(state)==before
            print(root.name,[k for k,v in checks.items() if not v],flush=True)
    # Prove the reported pre-fix failure through the preceding executable.
    before_state=out/'old-scene.state';run(out/'before',ROOT/'build/pride-launch2/player.exe',md,1,'aot',save=before_state)
    checks['previous_player_cannot_save_level1']=not before_state.exists()
    paths=[Path(__file__),build_path,old_path,source,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=counts,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
