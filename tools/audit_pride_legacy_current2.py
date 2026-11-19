"""Author each private control with its own executable identity before replay."""
from pathlib import Path

first_audit=Path(__file__).with_name('audit_pride_legacy_current.py')
source=first_audit.read_text().replace("out=base/'current-format'","out=base/'current-format2'")
needle="        commands[case]=cmd;env=environment(folder);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')"
assert source.count(needle)==1
source=source.replace(needle,'''        if host=='mixed':
            author=folder/'author';author.mkdir();prior_state=author/'current.state'
            seed=list(r['commands']['author']);seed[0]=str(binary);seed[seed.index('--save-at')+2]=str(prior_state)
            with (author/'run.log').open('wb') as log:
                result=subprocess.run(seed,cwd=ROOT,env=environment(author),stdout=log,stderr=subprocess.STDOUT,timeout=180)
            assert not result.returncode and prior_state.read_bytes()[:8]==b'PRHSAVE1'
            cmd[cmd.index('--load')+1]=str(prior_state);commands[case+'-author']=seed
        commands[case]=cmd;env=environment(folder);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')''')
source=source.replace('paths=[Path(__file__),build_path]','paths=[Path(__file__),first_audit,build_path]')
exec(compile(source,str(first_audit),'exec'))
