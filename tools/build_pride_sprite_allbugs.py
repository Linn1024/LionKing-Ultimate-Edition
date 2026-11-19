"""Build the tracked-field observer using only the fresh HUD player's objects."""
from pathlib import Path

original = Path(__file__).with_name('build_pride_installed_allbugs.py')
source = original.read_text()

def change(before, after):
    global source
    assert source.count(before) == 1, before
    source = source.replace(before, after)

change("base = ROOT/'build/pride-installed-cache41'", "base = ROOT/'build/pride-sprite-fresh44'")
change("cwd = ROOT/'build/pride-final-standalone'", 'cwd = base')
change("cmd = previous['compiles']['host'].copy()", """rows = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe', '-t', 'compdb', '-x'], cwd=base))
    host_entries = [r for r in rows if r.get('output', '').replace('\\\\', '/').endswith('/pride_final_host.c.obj')]
    assert len(host_entries) == 1
    host_entry = host_entries[0]
    host_command = argv(host_entry['command'])
    cmd = host_command.copy()""")
change("compile_command = previous['compiles']['host'].copy()", 'compile_command = host_command.copy()')
change("(cwd/p).resolve() == base/'host.obj'", "(cwd/p).resolve() == (base/host_entry['output']).resolve()")
change('assert unchanged == 320 and len(all_inputs) == 321', 'assert unchanged == 321 and len(all_inputs) == 322')
change("paths = [Path(__file__), ROOT/'tools/build_pride_rng_allbugs.py'",
       "paths = [Path(__file__), original, ROOT/'tools/build_pride_rng_allbugs.py'")

exec(compile(source, str(original), 'exec'))
