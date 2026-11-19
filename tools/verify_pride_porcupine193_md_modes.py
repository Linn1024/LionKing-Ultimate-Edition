"""Production source/mode verification of all three MD attack-timing contacts."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_porcupine188_modes.py')
source=verifier_source.read_text().replace('pride-porcupine186-polled','pride-porcupine191-md-timing').replace('pride-porcupine187-difficulty','pride-porcupine192-md-timing').replace('pride-porcupine188-modes','pride-porcupine193-md-modes')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
