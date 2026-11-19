"""Try the retained original-MD controller route with matching entry randomness."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_launch_completion.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-rng-player2'")
source=source.replace("base/'completion'","base/'completion-reference'").replace('for width in (320,256):','for width in (320,):')
source=source.replace('gameplay.levels.pride_lands.health_death = md\\n','gameplay.levels.pride_lands.health_death = md\\ngameplay.levels.pride_lands.random_entry = md\\n')
old="        tape=ROOT/previous['tape'];assert digest(tape)==previous['tape_sha256']"
new="        tape=ROOT/'build/pride-ground-gap/native/derived.polled.tape';assert digest(tape)=='216040df88f794e740f4a551a11ffdee8762754e9e04f93d419d7b706f7bf1c4';previous['frames']=5500"
assert source.count(old)==1
source=source.replace(old,new).replace('sources=[Path(__file__),bp]','sources=[Path(__file__),original_verifier,bp]')
exec(compile(source,str(original_verifier),'exec'))
