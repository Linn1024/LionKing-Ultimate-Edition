"""Exercise the standalone player against ordinary completion and preceding native/mixed cases."""
from pathlib import Path

guest_verifier = Path(__file__).with_name('verify_pride_owned_guest_replays.py')
source = guest_verifier.read_text().replace('build/pride-owned-guest2', 'build/pride-player')
source = source.replace("'original': original}", "'original': original, 'guest_verifier': guest_verifier}")
source = source.replace('paths=[Path(__file__),original,bp,', 'paths=[Path(__file__),guest_verifier,original,bp,')
source = source.replace('paths=[Path(__file__),original,build_path,', 'paths=[Path(__file__),guest_verifier,original,build_path,')
exec(compile(source, str(guest_verifier), 'exec'))
