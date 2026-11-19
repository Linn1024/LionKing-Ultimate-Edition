"""Observe native default revival on the existing controller-only level route."""
from pathlib import Path

original_verifier=Path(__file__).with_name('capture_pride_rng_native.py')
source=original_verifier.read_text().replace("base/'native'","base/'native-default'")
start=source.index("    cases=[");end=source.index('    paths=[',start)
source=source[:start]+"    cases=[('default',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape',3500,False)]\n"+source[end:]
source=source.replace('paths=[Path(__file__),bp]','paths=[Path(__file__),original_verifier,bp]')
exec(compile(source,str(original_verifier),'exec'))
