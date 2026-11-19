"""A pre-game native save permits a different Pride health-death selection."""
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
    base=ROOT/'build/pride-launch4';bp=base/'build-report.json';build=bound(bp)
    out=base/'menu-source';out.mkdir();state=base/'menu-save/aot/menu.state';before=digest(state)
    profile=out/'resources.ini';original=ROOT/'profiles/pride-development-preview.ini'
    profile.write_text(original.read_text().replace('gameplay.levels.pride_lands.health_death = md','gameplay.levels.pride_lands.health_death = snes'))
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n');tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
         '--config',cfg,'--input',tape,'--load',state,'--frames',3000,'--no-audio','--no-pace','--no-record',
         '--hash-at',','.join(map(str,range(601,3001))),'--wav',out/'audio.wav','--wav-seconds',100,
         '--dump-window',out/'window.png','--dump-png',out/'guest.png']
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    with (out/'run.log').open('wb') as log:r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    reference=ROOT/'build/pride-launch3/regression/mixed-native';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual=re.findall(pattern,(out/'run.log').read_text());expected=[row for row in re.findall(pattern,(reference/'run.log').read_text()) if int(row[0])>600]
    audio=wav_data(out/'audio.wav');checks=dict(exit=not r.returncode,every_field=len(actual)==2400 and actual==expected,
        entire_pcm=bool(audio) and audio==wav_data(reference/'audio.wav')[-len(audio):],
        whole_guest=pixels(out/'guest.png')==pixels(reference/'guest.png'),whole_client=pixels(out/'window.png')==pixels(reference/'window.png'),
        input_preserved=digest(state)==before)
    paths=[Path(__file__),bp,state,base/'menu-save/report.json',ROOT/'build/pride-launch3/regression/report.json',original,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=list(map(str,cmd)),native_fields_compared=len(actual),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
