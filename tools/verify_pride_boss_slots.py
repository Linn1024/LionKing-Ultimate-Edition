"""Use real F1/F5 in ordinary boss play, without a practice start or state load."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_preview_slots.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch2'", "ROOT/'build/pride-rng-player4'")
source=source.replace("base/'preview-package-audit.json'", "base/'build-report.json'")
source=source.replace("ROOT/'dist/development-preview/LionKing.exe'", "base/'player.exe'")
source=source.replace("base/'preview-slots'", "base/'boss-slots'")
source=source.replace("ROOT/'profiles/pride-development-preview.ini'", "ROOT/'build/pride-rng-player2/completion-reference-unpaused256/256/resources.ini'")
source=source.replace("ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'", "ROOT/'build/pride-rng-player3/width-arena-input/route.polled.tape'")
old="'--input',tape,'--practice-level',0,'--frames',1700"
assert old in source
source=source.replace(old,"'--input-polled',tape,'--frames',2900")
source=source.replace('range(1,1701)','range(1,2901)').replace("r['field']>=1600", "r['field']>=2800")
source=source.replace('1600<=saved<1615','2800<=saved<2815')
source=source.replace('((field+1)*48000*357366//21477272)', '(field*48000*357366//21477272)')
source=source.replace('paths=[Path(__file__),package_path,', 'paths=[Path(__file__),original_verifier,package_path,')
exec(compile(source,str(original_verifier),'exec'))
