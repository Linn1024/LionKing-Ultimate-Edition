"""The familiar Mixed Graphics CMD on the published hyena voice build."""
from pathlib import Path
verifier_source=Path(__file__).with_name('capture_pride_mixed_launcher66.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-launchers66'","ROOT/'build/pride-hyena-voice72'")
source=source.replace("source=base/'report.json'","source=base/'publication/report.json'")
source=source.replace("out=base/'windows'","out=base/'mixed-window'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
