"""Exercise both staged frontends, including actual SDL virtual tree input."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_singlepass_remap.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-tree-help'")
source=source.replace('paths=[Path(__file__)]','paths=[Path(__file__),original_verifier]')
source=source.replace("checks[name+'/selftest']='remap_selftest: PASS (0 failed)' in (case/'run.log').read_text()", """checks[name+'/selftest']='remap_selftest: PASS (0 failed)' in (case/'run.log').read_text()
        text=(case/'run.log').read_text()
        for label in ('virtual A edits branch inheritance and contrary leaf override','virtual X Apply rejects unsupported draft',
                      'virtual Y opens complete paged scope and fallback text','virtual d-pad pages help without moving tree',
                      'SDL wheel pages modal without moving tree','virtual editor test preserves every applied resource choice'):
            checks[name+'/'+label]='remap_selftest: ok   '+label in text""")
exec(compile(source,str(original_verifier),'exec'))
