"""Retain cold native/mixed/revival cases after the private host-I/O change."""
from pathlib import Path

native_verifier=Path(__file__).with_name('verify_pride_rng_native_regression.py')
source=native_verifier.read_text().replace("ROOT/'build/pride-rng-player'", "ROOT/'build/pride-rng-player3'")
source=source.replace('paths=[Path(__file__),original_verifier,',
                      'paths=[Path(__file__),original_verifier,native_verifier,')
exec(compile(source,str(native_verifier),'exec'))
