"""Compare every directly linked predecessor object with its standalone rebuild."""
from pathlib import Path

original_verifier = Path(__file__).with_name('verify_pride_owned_core_code.py')
source = original_verifier.read_text().replace("ROOT / 'build/pride-owned-core'", "ROOT / 'build/pride-player'")
source = source.replace("out = base / 'code-equivalence'", "out = base / 'code-equivalence2'")
# C++ COMDAT section names can exceed Windows filename limits. The comparison
# still uses each full section name; only the diagnostic output name is hashed.
source = source.replace("section.replace('$', '_')", "__import__('hashlib').sha256(section.encode()).hexdigest()[:16]")
needle = '    build = bound(bp)'
assert source.count(needle) == 1
source = source.replace(needle, needle + '''
    previous = ROOT / 'build/pride-owned-guest2/build-report.json'
    old = bound(previous)
    replacements = {}
    for name, sha in old['link_inputs_sha256'].items():
        if not name.endswith('.obj'):
            continue
        assert digest(ROOT / name) == sha
        matches = [p for p in build['source_objects'] if Path(p).name == Path(name).name]
        for component in ('/snesrecomp/runner/', '/recomp-ui/'):
            if component in name:
                matches = [p for p in matches if component in p]
        if len(matches) > 1:
            matches = [p for p in matches if '/CMakeFiles/tlk_pride_player.dir/' in p]
        assert len(matches) == 1, (name, matches)
        replacements[name] = matches[0]
    assert len(replacements) == 305
    build['replacements'] = replacements
''')
source = source.replace('paths = [Path(__file__), bp]', 'paths = [Path(__file__), original_verifier, bp, previous]')
exec(compile(source, str(original_verifier), 'exec'))
