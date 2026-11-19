"""Verify cross-editor replay under the ordered-component contract."""
from pathlib import Path

first_verifier=Path(__file__).with_name('verify_pride_save_identity.py')
source=first_verifier.read_text().replace("ROOT/'build/pride-save-identity'","ROOT/'build/pride-save-identity2'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),first_verifier,')
exec(compile(source,str(first_verifier),'exec'))
