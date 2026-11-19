"""Exercise the owned eligibility predicate on ordinary boss/card continuations."""
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    # Keep successful predecessors frozen, with each subprocess binding this
    # wrapper and its original verifier into the new report.
    for name, old_base in (('verify_pride_boss_save.py', 4), ('verify_pride_card_save.py', 5)):
        original = Path(__file__).with_name(name)
        code = original.read_text().replace(f"base=ROOT/'build/pride-rng-player{old_base}'",
                                            "base=ROOT/'build/pride-rng-player7'")
        if old_base == 4:
            code = code.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original,bp,')
        else:
            code = code.replace('paths=[Path(__file__),original_verifier,card_snapshot,bp,',
                                'paths=[Path(__file__),original,original_verifier,card_snapshot,bp,')
        # The card verifier expands another verifier. Execute the expansion in
        # this process so its own explicit source bindings stay intact.
        exec(compile(code, str(original), 'exec'),
             {'__name__': '__main__', '__file__': __file__, 'original': original})


if __name__ == '__main__':
    main()
