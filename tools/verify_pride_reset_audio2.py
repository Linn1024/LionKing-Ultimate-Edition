"""Run selected MD audio reset checks with a verified installed sound backend."""
from pathlib import Path

original_audio_verifier = Path(__file__).with_name('verify_pride_reset_audio.py')
source = original_audio_verifier.read_text().replace('build/pride-reset/audio-views', 'build/pride-reset/audio-views2')
source = source.replace('"paths=(Path(__file__),wrapped_verifier,', '"paths=(Path(__file__),original_audio_verifier,ROOT/\'build/pride-reset/audio-views2/genesis_plus_gx_libretro.dll\',wrapped_verifier,')
source = source.replace("audio_checks = '''", "source = source.replace('        assert r.returncode==0,', \"        assert 'MD sound library unavailable' not in (folder/'run.log').read_text() and 'Profile rejected' not in (folder/'run.log').read_text(), name\\n        assert r.returncode==0,\")\naudio_checks = '''")
exec(compile(source, str(original_audio_verifier), 'exec'))
