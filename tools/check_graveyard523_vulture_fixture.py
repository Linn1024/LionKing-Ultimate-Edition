"""Continue the current mid-level save to the first active vulture section."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard522_enemy_fixture.py')
s=template.read_text().replace("reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference);assert r['result']=='PASS'", "reference=ROOT/'build/graveyard522-enemies/report.json';r=bound(reference);assert r['result']=='ENEMY_FIXTURE_AUTHORED'")
s=s.replace('build/graveyard522-enemies','build/graveyard523-vultures').replace("reference=ROOT/'build/graveyard523-vultures/report.json'", "reference=ROOT/'build/graveyard522-enemies/report.json'")
s=s.replace("cmd=r['command'].copy()", "cmd=r['command'].copy()\nused=int(re.search(r'tape_words_used=(\\d+)',(reference.parent/'run.log').read_text()).group(1))\nsource=Path(cmd[cmd.index('--input-polled')+1]);suffix=out/'after14250.polled.tape';suffix.write_bytes(source.read_bytes()[used*2:]);cmd[cmd.index('--input-polled')+1]=str(suffix);cmd[cmd.index('--load')+1]=str(reference.parent/'enemies.state')")
s=s.replace("i=cmd.index('--wav');del cmd[i:i+2];i=cmd.index('--wav-seconds');del cmd[i:i+2]", '')
s=s.replace("'14250'", "'15000'")
s=s.replace('paths=[Path(__file__),reference,', 'paths=[Path(__file__),template,source,reference,')
exec(compile(s,str(template),'exec'))
