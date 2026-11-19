"""Normal-entry component leaves native revival and all CPU state intact."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_rng_component.py')
source=original_verifier.read_text().replace("base/'component2'","base/'entry-component'")
source=source.replace('rng_policy_oracle.dll','rng_entry_oracle.dll').replace('rng_scene_original','rng_entry_original')
source=source.replace("                        elif descriptor in (0xc00387,0xc0080d):expected=seed\n",'')
source=source.replace("ROOT/'tools/pride_rng_policy_oracle.c'", "ROOT/'tools/pride_rng_entry_oracle.c',ROOT/'tools/pride_rng_policy_oracle.c'")
source=source.replace('tlk_rng_scene.c','tlk_rng_entry.c').replace('tlk_rng_scene.h','tlk_rng_entry.h')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
