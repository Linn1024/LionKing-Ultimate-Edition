"""Exercise actual ordinary F1/F5 after the maintained runtime/presenter rebuild."""
from pathlib import Path

card_verifier = Path(__file__).with_name('verify_pride_card_slots.py')
source = card_verifier.read_text().replace('build/pride-rng-player5', 'build/pride-owned-core')
source = source.replace('paths=[Path(__file__),original_verifier,boss_verifier,package_path,',
                        'paths=[Path(__file__),card_verifier,original_verifier,boss_verifier,package_path,')
exec(compile(source, str(card_verifier), 'exec'))
