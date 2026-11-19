"""Exercise ordinary complete routes with the new independent MD entry seed."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_launch_completion.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-rng-player'")
source=source.replace('gameplay.levels.pride_lands.health_death = md\\n','gameplay.levels.pride_lands.health_death = md\\ngameplay.levels.pride_lands.random_entry = md\\n')
source=source.replace('sources=[Path(__file__),bp]','sources=[Path(__file__),original_verifier,bp]')
exec(compile(source,str(original_verifier),'exec'))
