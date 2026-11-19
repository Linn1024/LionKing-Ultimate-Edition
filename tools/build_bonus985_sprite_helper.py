"""Prepare1253 images and924 pose bounds, with preceding records preserved."""
from pathlib import Path
template=Path(__file__).with_name('build_later882_helper.py');s=template.read_text().replace('build/later882-helper','build/bonus985-sprite-helper')
s=s.replace("ROOT/'tools/later_actor_pairs.json',","ROOT/'tools/later_actor_pairs.json',ROOT/'tools/pride_actor_pairs.json',ROOT/'tools/bonus_actor_pairs.json',")
exec(compile(s,str(template),'exec'))
