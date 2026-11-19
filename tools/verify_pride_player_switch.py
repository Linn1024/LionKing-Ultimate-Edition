"""Exercise actual live SNES/MD/SNES resource editing on the standalone player."""
from pathlib import Path

original_verifier = Path(__file__).with_name('verify_pride_launch_switch.py')
source = original_verifier.read_text().replace("ROOT/'build/pride-launch2'", "ROOT/'build/pride-player'")
source = source.replace('paths=[Path(__file__),build_path,', 'paths=[Path(__file__),original_verifier,build_path,')
exec(compile(source, str(original_verifier), 'exec'))
