"""Exercise the new two-level combined selection and actual Windows regions."""
from pathlib import Path
template=Path(__file__).with_name('audit_next728_route.py')
s=template.read_text().replace('build/next729-route','build/next748-route').replace('build/next727-observer/player.exe','build/next747/player.exe').replace('build/graveyard707-helper/sprites.assets','build/next741-helper/sprites.assets')
s=s.replace("TLK_AUDIO_EVENTS=str(out/'events.csv')", "TLK_SPRITE_REPORT=str(out/'sprites.json'),TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_LIZARD_ATTACK_TRACE=str(out/'lizard.csv'),TLK_LIZARD_DEFEAT_TRACE=str(out/'defeat.csv'),TLK_LEAF_TRACE=str(out/'leaves.csv')")
exec(compile(s,str(template),'exec'))
