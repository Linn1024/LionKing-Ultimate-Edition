"""Replay ordinary completion and both complete-cache save scenes on the clean host."""
from pathlib import Path


def main():
    for name in ('verify_pride_width_completion.py', 'verify_pride_boss_save.py', 'verify_pride_card_save.py'):
        original = Path(__file__).with_name(name)
        code = original.read_text()
        if name == 'verify_pride_card_save.py':
            code = code.replace("base=ROOT/'build/pride-rng-player5'", "base=ROOT/'build/pride-owned-host3'")
            code = code.replace('paths=[Path(__file__),original_verifier,card_snapshot,bp,',
                                'paths=[Path(__file__),original,original_verifier,card_snapshot,bp,')
        else:
            code = code.replace("base=ROOT/'build/pride-rng-player4'", "base=ROOT/'build/pride-owned-host3'")
            if name == 'verify_pride_width_completion.py':
                code = code.replace("author=base/'width-fight1/report.json'", "author=ROOT/'build/pride-rng-player4/width-fight1/report.json'")
                code = code.replace("tape=base/'width-fight1/best.polled.tape'", "tape=ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape'")
                code = code.replace("end=base/'width-fight-cold-end/report.json'", "end=ROOT/'build/pride-rng-player4/width-fight-cold-end/report.json'")
            code = code.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original,bp,')
        exec(compile(code, str(original), 'exec'),
             {'__name__': '__main__', '__file__': __file__, 'original': original})


if __name__ == '__main__':
    main()
