"""Actual first-hit Windows clients with MD attack timing on all difficulties."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_porcupine190_windows.py')
source=verifier_source.read_text().replace('pride-porcupine186-polled','pride-porcupine191-md-timing').replace('pride-porcupine187-difficulty','pride-porcupine192-md-timing').replace('pride-porcupine190-windows','pride-porcupine194-md-windows')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
