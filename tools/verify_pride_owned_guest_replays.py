"""Verify ordinary mixed completion and retained native/mixed playback on fresh guest banks."""
from pathlib import Path


def main():
    for name in ('verify_pride_width_completion.py', 'verify_pride_scene_save_regression.py'):
        original = Path(__file__).with_name(name)
        source = original.read_text()
        if name == 'verify_pride_width_completion.py':
            source = source.replace("base=ROOT/'build/pride-rng-player4'", "base=ROOT/'build/pride-owned-guest2'")
            for fragment in ('width-fight1/report.json', 'width-fight1/best.polled.tape', 'width-fight-cold-end/report.json'):
                source = source.replace("base/'" + fragment + "'", "ROOT/'build/pride-rng-player4/" + fragment + "'")
            source = source.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original,bp,')
        else:
            source = source.replace("ROOT/'build/pride-launch3'", "ROOT/'build/pride-owned-guest2'")
            source = source.replace('paths=[Path(__file__),build_path,', 'paths=[Path(__file__),original,build_path,')
        exec(compile(source, str(original), 'exec'),
             {'__file__': __file__, '__name__': '__main__', 'original': original})


if __name__ == '__main__':
    main()
