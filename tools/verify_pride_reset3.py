"""Run full reset replay or ordinary-host regressions on the cache correction."""
import argparse
from pathlib import Path
import sys

from audit_scenes import ROOT

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--scope',choices=('headless','sdl','md-audio','early','windows'),required=True)
args=parser.parse_args()
if args.scope in ('early','windows'):
    tool='verify_pride_clock_early_state.py' if args.scope=='early' else 'verify_pride_clock_native_windows.py'
    original_verifier=ROOT/'tools'/tool
    source=original_verifier.read_text().replace('build/pride-restart-clock/native','build/pride-reset/fixed3')
    source=source.replace('Path(__file__),build_path','Path(__file__),original_verifier,build_path')
else:
    original_verifier=ROOT/'tools/verify_pride_reset_run.py'
    source=original_verifier.read_text().replace('build/pride-reset/views','build/pride-reset/'+('audio3' if args.scope=='md-audio' else 'views3'))
    source=source.replace('paths=(Path(__file__),','paths=(Path(__file__),original_verifier,')
    sys.argv=[sys.argv[0],'--host','headless' if args.scope=='headless' else 'sdl']
    if args.scope=='md-audio':
        anchor="profile.write_text('schema = 1\\ngame = snes\\n')";assert source.count(anchor)==1
        source=source.replace(anchor,"profile.write_text('schema = 1\\ngame = snes\\n'+''.join(line+'\\n' for line in (ROOT/'build/pride-source-live/seeded/resources.ini').read_text().splitlines() if line.startswith('audio.') and line.endswith('= md')))")
        source=source.replace("cmd=[binary,'--rom'","cmd=[binary,'--md-rom',ROOT/'Lion King, The (World).md','--rom'")
        source=source.replace('env.update(TLK_RESET_PROBE=',"env.update(TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_RESET_PROBE=")
        source=source.replace('        assert r.returncode==0,',"        assert 'MD sound library unavailable' not in (folder/'run.log').read_text() and 'Profile rejected' not in (folder/'run.log').read_text(), name\n        assert r.returncode==0,")
        audio_checks='''    import csv
    def stems(folder):
        with (folder/'stems.csv').open() as stream:
            return [r for r in csv.DictReader(stream) if r['samples'].isdigit()]
    for name in commands:
        rows=stems(out/name)
        checks[name+'/audible_md']=any(int(r['md_peak'])>0 for r in rows)
        if name.startswith('none-'):continue
        kind,mode,warm=name.split('-');split=0
        if warm=='1211':
            boundaries=[i for i in range(1,len(rows)) if int(rows[i]['frame'])<int(rows[i-1]['frame'])]
            checks[name+'/warm_driver_audible']=bool(boundaries) and any(int(r['md_peak'])>0 for r in rows[:boundaries[0]])
            if boundaries:split=boundaries[0]
        checks[name+'/replayed_stems']=rows[split:]==stems(controls[mode])
'''
        source=source.replace('    paths=(Path(__file__),',audio_checks+'    paths=(Path(__file__),')
        source=source.replace('paths=(Path(__file__),',"paths=(Path(__file__),ROOT/'build/pride-source-live/seeded/resources.ini',ROOT/'build/pride-reset/audio3/genesis_plus_gx_libretro.dll',")
        source=source.replace('selected_md_audio_reset_verified=False','selected_md_audio_reset_verified=all(checks.values())')
exec(compile(source,str(original_verifier),'exec'))
