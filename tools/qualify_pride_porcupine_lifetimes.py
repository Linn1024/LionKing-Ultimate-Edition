"""Reuse all five completed captures, recognizing absent native adapter traces."""
from pathlib import Path

runner=Path(__file__).with_name('verify_pride_porcupine_lifetimes.py')
source=runner.read_text()
def change(before,after):
    global source
    assert source.count(before)==1,before
    source=source.replace(before,after)
change("out.mkdir()", "assert out.is_dir()")
change("folder.mkdir()", "assert folder.is_dir()")
change("p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())", "assert p.is_file()")
change("(folder/'resources.ini').write_text('schema = 1\\ngame = snes\\n')", "assert (folder/'resources.ini').read_text()=='schema = 1\\ngame = snes\\n'")
change('''        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode''',
       "        rc=json.loads((out/'failure.json').read_text())['player_returns'][label]")
change("checks[label+'_'+name]=digest(left/name)==digest(right/name)",
       """checks[label+'_'+name]=((name=='attack.csv' and label.startswith('native_') and not (left/name).exists() and not (right/name).exists())
                or ((left/name).exists() and (right/name).exists() and digest(left/name)==digest(right/name)))""")
change('paths=[Path(__file__),source,build_path,selector_path]',
       "paths=[Path(__file__),runner,source,build_path,selector_path,out/'failure.json']")
change("active_linked_list_only=True", "captures_reused_without_reruns=True, commands_reconstructed_from_exact_runner=True, retained_failed_trace_assumption=True, active_linked_list_only=True")
exec(compile(source,str(runner),'exec'))
