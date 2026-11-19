"""Verify roar behavior timing and independent sound through actual SDL mixing."""
import csv
import json
import os
import subprocess
import wave
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out = ROOT/'build/pride-roar-audio'
    out.mkdir(parents=True, exist_ok=True)
    config = out/'host.ini'
    config.write_text('opengl = 1\nscale = 2\n')
    tape = ROOT/'build/pride-roar-behavior/input.tape'
    assert tape.is_file(), 'Run verify_pride_roar_behavior.py first'
    base = [str(ROOT/'dist/LionKing.exe'), '--rom', str(ROOT/'Lion King, The (USA).sfc'),
            '--md-rom', str(ROOT/'Lion King, The (World).md'), '--config', str(config),
            '--no-pace', '--no-audio', '--no-record']
    runs = {}
    for scenario in ('native', 'md-native-voice', 'md-voice', 'md-voice-lle'):
        profile = out/(scenario+'.ini')
        profile.write_text('schema = 1\ngame = snes\naudio.music.pride_lands = md\n'
                           + ('gameplay.simba.roar = md\n' if scenario != 'native' else '')
                           + ('audio.effects.simba.roar = md\n' if scenario.startswith('md-voice') else ''))
        if scenario == 'native':
            state = out/'native-ready.state'
            with (out/'prepare.log').open('wb') as log:
                subprocess.run([*base, '--resource-profile', str(profile), '--practice-level', '0',
                                '--frames', '2200', '--save-at', '2200', str(state)], cwd=ROOT,
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        else:
            state = ROOT/'build/pride-roar-behavior/snes-ready.state'
        env = os.environ.copy()
        env.update(TLK_AUDIO_EVENTS=str(out/(scenario+'-events.csv')),
                   TLK_AUDIO_STEMS=str(out/(scenario+'-stems.csv')),
                   TLK_MD_SOUND_COMMANDS=str(out/(scenario+'-commands.csv')))
        logfile = out/(scenario+'.log')
        wav = out/(scenario+'.wav')
        with logfile.open('wb') as log:
            subprocess.run([*base, '--resource-profile', str(profile), '--load', str(state),
                            '--input', str(tape), '--frames', '2584', '--wav', str(wav),
                            '--wav-seconds', '10', *(['--lle'] if scenario.endswith('-lle') else [])],
                           cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        events = list(csv.DictReader((out/(scenario+'-events.csv')).open()))
        voice = [int(row['frame']) for row in events if row['event'] == '0005' and row['actor'] == 'b213']
        assert len(voice) == 1, (scenario, voice)
        commands = list(csv.DictReader((out/(scenario+'-commands.csv')).open()))
        pcm = [int(row['value']) for row in commands if row['selector'] == '19']
        assert pcm == ([10] if scenario.startswith('md-voice') else []), (scenario, pcm)
        stems = list(csv.DictReader((out/(scenario+'-stems.csv')).open()))
        window = [row for row in stems if voice[0]+1 <= int(row['frame']) <= voice[0]+100]
        assert window
        native_peak = max(int(row['native_peak']) for row in window)
        if scenario.startswith('md-voice'):
            assert native_peak == 0, (scenario, 'Native voice leaked', native_peak)
        else:
            assert native_peak > 1000, (scenario, 'Native voice inaudible', native_peak)
        with wave.open(str(wav), 'rb') as stream:
            assert stream.getnchannels() == 2 and stream.getframerate() == 48000
            audio = stream.readframes(stream.getnframes())
            assert len(audio) > 1000000
        runs[scenario] = {'voice_frame':voice[0], 'native_peak':native_peak,
                          'pcm':pcm, 'hashes':hashes(logfile), 'audio':audio}
        print(scenario, 'one audible chosen roar at frame', voice[0], 'PASS', flush=True)
    assert runs['native']['voice_frame'] - runs['md-native-voice']['voice_frame'] == 2
    assert runs['md-native-voice']['voice_frame'] == runs['md-voice']['voice_frame']
    assert runs['md-native-voice']['audio'] != runs['md-voice']['audio']
    assert runs['md-voice']['audio'] == runs['md-voice-lle']['audio']
    assert runs['md-voice']['hashes'] == runs['md-voice-lle']['hashes']
    report = {'result':'PASS', 'scope':__doc__, 'runs':{
        name:{key:value for key,value in row.items() if key != 'audio'} for name,row in runs.items()}}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
