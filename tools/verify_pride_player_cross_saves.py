"""Exercise active boss and inactive card source/save rules across the new build."""
from pathlib import Path

host_verifier = Path(__file__).with_name('verify_pride_owned_save_context.py')
source = host_verifier.read_text().replace('build/pride-rng-player7', 'build/pride-player')
source = source.replace("'original': original}", "'original': original, 'host_verifier': host_verifier}")
source = source.replace('paths=[Path(__file__),original,bp,', 'paths=[Path(__file__),host_verifier,original,bp,')
source = source.replace('paths=[Path(__file__),original,original_verifier,card_snapshot,bp,',
                        'paths=[Path(__file__),host_verifier,original,original_verifier,card_snapshot,bp,')
exec(compile(source, str(host_verifier), 'exec'))
