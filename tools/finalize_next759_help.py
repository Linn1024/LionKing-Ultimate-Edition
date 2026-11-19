"""Keep resource help consistent with actual fourth/fifth-level eligibility."""
from audit_scenes import ROOT
p=ROOT/'engine/runner/tlk_resources.c';s=p.read_text()
s=s.replace("Elephant Graveyard and Simba's Exile; native fallback", "Elephant Graveyard, reviewed Stampede running frames and Simba's Exile; native fallback")
s=s.replace('Pride Lands ground-lizard attack: original MD FM124', 'Pride Lands/Exile chameleon attack: original MD FM124')
s=s.replace('Pride Lands and Elephant Graveyard bonus bug','Pride Lands, Elephant Graveyard and Exile bonus bug')
s=s.replace('Pride Lands and Elephant Graveyard health pickup','Pride Lands, Elephant Graveyard and Exile health pickup')
s=s.replace('Pride Lands and Elephant Graveyard full-health pickup','Pride Lands, Elephant Graveyard and Exile full-health pickup')
s=s.replace('Pride Lands and Elephant Graveyard cub hurt cry','Pride Lands, Elephant Graveyard and Exile cub hurt cry')
s=s.replace('Pride Lands and Elephant Graveyard cub roar','Pride Lands, Elephant Graveyard and Exile cub roar')
s=s.replace('Pride Lands and Elephant Graveyard; MD activation14', 'Pride Lands, Elephant Graveyard and Exile; MD activation14')
p.write_text(s)
