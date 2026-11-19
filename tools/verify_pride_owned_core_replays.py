"""Run the real completion/save gates after rebuilding all non-guest staged objects."""
from pathlib import Path

host_verifier = Path(__file__).with_name('verify_pride_owned_host_replays.py')
source = host_verifier.read_text().replace('build/pride-owned-host3', 'build/pride-owned-core')
# The expanded verifier already binds the original completion/boss/card sources.
source = source.replace("'original': original}", "'original': original, 'host_verifier': host_verifier}")
source = source.replace("code = code.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original,bp,')",
                        "code = code.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original,host_verifier,bp,')")
source = source.replace("'paths=[Path(__file__),original,original_verifier,card_snapshot,bp,'",
                        "'paths=[Path(__file__),host_verifier,original,original_verifier,card_snapshot,bp,'")
exec(compile(source, str(host_verifier), 'exec'))
