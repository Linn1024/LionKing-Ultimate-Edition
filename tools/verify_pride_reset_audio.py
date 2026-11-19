"""Compare complete reset replay with supported selected MD music/effects."""
from pathlib import Path

wrapped_verifier = Path(__file__).with_name('verify_pride_reset_run.py')
source = wrapped_verifier.read_text().replace('build/pride-reset/views', 'build/pride-reset/audio-views')
source = source.replace('paths=(Path(__file__),', "paths=(Path(__file__),wrapped_verifier,ROOT/'build/pride-source-live/seeded/resources.ini',")
anchor = "profile.write_text('schema = 1\\ngame = snes\\n')"
assert source.count(anchor) == 1
source = source.replace(anchor, "profile.write_text('schema = 1\\ngame = snes\\n'+''.join(line+'\\n' for line in (ROOT/'build/pride-source-live/seeded/resources.ini').read_text().splitlines() if line.startswith('audio.') and line.endswith('= md')))")
source = source.replace("cmd=[binary,'--rom'", "cmd=[binary,'--md-rom',ROOT/'Lion King, The (World).md','--rom'")
source = source.replace("out=base/'matrix'/args.host;", "assert args.host=='sdl';out=base/'matrix'/args.host;")
source = source.replace('env.update(TLK_RESET_PROBE=', "env.update(TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_RESET_PROBE=")
audio_checks = '''    import csv
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
source = source.replace('    paths=(Path(__file__),', audio_checks+'    paths=(Path(__file__),')
source = source.replace('selected_md_audio_reset_verified=False', 'selected_md_audio_reset_verified=all(checks.values())')
exec(compile(source, str(wrapped_verifier), 'exec'))
