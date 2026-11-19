"""Use real F1/F5 on the native level card after ordinary Pride completion."""
from pathlib import Path

boss_verifier=Path(__file__).with_name('verify_pride_boss_slots.py')
source=boss_verifier.read_text().replace('build/pride-rng-player4','build/pride-rng-player5')
source=source.replace("base/'boss-slots'", "base/'card-slots'")
source=source.replace('build/pride-rng-player3/width-arena-input/route.polled.tape',
                      'build/pride-rng-player4/width-fight1/best.polled.tape')
source=source.replace('2900','3100').replace('2901','3101').replace('2800','3000').replace('2815','3015')
source=source.replace('paths=[Path(__file__),original_verifier,package_path,',
                      'paths=[Path(__file__),original_verifier,boss_verifier,package_path,')
exec(compile(source,str(boss_verifier),'exec'))
