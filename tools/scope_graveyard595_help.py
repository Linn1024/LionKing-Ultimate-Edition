"""Update only implemented shared audio help; keep gameplay and graphics claims unchanged."""
from audit_scenes import ROOT
ids=('audio.effects.simba.roar','audio.effects.simba.hurt','audio.effects.simba.bounce','audio.effects.simba.roll','audio.effects.simba.ledge_grab','audio.effects.world.hyena_hurt','audio.effects.world.hyena_pant','audio.effects.world.hyena_jump','audio.effects.world.hyena_taunt','audio.effects.world.bonus_bug','audio.effects.world.checkpoint','audio.effects.world.health_bug','audio.effects.world.full_health_bug','audio.effects.world.life_bug','audio.effects.world.roar_bug','audio.effects.world.harmful_bug','audio.effects.world.pickup_arrival')
p=ROOT/'engine/runner/tlk_resources.c';lines=p.read_text().splitlines(keepends=True)
for i,line in enumerate(lines):
    if any('"'+id+'",' in line for id in ids):
        lines[i]=line.replace("Pride Lands and Can't Wait to Be King",'Pride Lands, Can\'t Wait to Be King and Elephant Graveyard') if "Pride Lands and Can't Wait to Be King" in line else line.replace('Pride Lands','Pride Lands and Elephant Graveyard')
p.write_text(''.join(lines))
p=ROOT/'engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks';s=p.read_text();s=s.replace("Pride Lands and Can't Wait to Be King cub Continue-token pickup", "Pride Lands, Can't Wait to Be King and Elephant Graveyard cub Continue-token pickup");p.write_text(s)
