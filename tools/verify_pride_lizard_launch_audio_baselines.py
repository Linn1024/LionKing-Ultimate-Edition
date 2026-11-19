"""Resolve source-specific baselines using the actual preceding bounce player.

Retain the failed first report: changing the pre-existing bounce replacement
is not expected to preserve native audio guest state. New launch neutrality
must hold against the same existing bounce selection, verified in the old build.
"""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    rp=base/'launch-audio/report.json';reference=bound(rp)
    wrong={f'{mode}/{name}/native_{kind}' for mode in ('aot','lle')
        for name in ('bounce','both') for kind in ('guest','client')}
    assert reference['result']=='FAIL'
    assert {k for k,v in reference['checks'].items() if not v}==wrong
    out=base/'launch-audio-baselines';out.mkdir()
    old=ROOT/'build/pride-ledge-work/player/player.exe'
    archive_path=ROOT/'build/pride-lizard-launch-baseline/report.json'
    assert digest(old)==bound(archive_path)['preview_player_sha256']
    command=list(reference['commands']['bounce-aot']);command[0]=str(old)
    for flag,name in (('--wav','audio.wav'),('--dump-window','window.png')):
        command[command.index(flag)+1]=str(out/name)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    with (out/'run.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks={k:v for k,v in reference['checks'].items() if k not in wrong}
    for mode in ('aot','lle'):
        bounce=base/f'launch-audio/bounce-{mode}';both=base/f'launch-audio/both-{mode}'
        checks[mode+'/launch_preserves_bounce_guest']=rows(both)==rows(bounce)
        checks[mode+'/launch_preserves_bounce_client']=pixels(both/'window.png')==pixels(bounce/'window.png')
        checks[mode+'/preceding_bounce_every_field']=len(rows(out))==4500 and rows(out)==rows(bounce)
        checks[mode+'/preceding_bounce_whole_pcm']=wav_data(out/'audio.wav')==wav_data(bounce/'audio.wav')
        checks[mode+'/preceding_bounce_actual_client']=pixels(out/'window.png')==pixels(bounce/'window.png')
    paths=[Path(__file__),rp,archive_path,old]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=command,
        events=reference['events'],command_counts=reference['command_counts'],
        retained_first_report='launch-audio/report.json',
        baseline_correction='New launch preserves native or pre-existing bounce selection; actual preceding bounce control verifies the latter.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
