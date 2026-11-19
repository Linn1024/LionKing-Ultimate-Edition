"""Capture final Graveyard hyena ownership from the existing current mid-level save."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard522_enemy_fixture.py')
s=template.read_text().replace("reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference);assert r['result']=='PASS'", "reference=ROOT/'build/graveyard523-vultures/report.json';r=bound(reference);assert r['result']=='ENEMY_FIXTURE_AUTHORED'")
s=s.replace('build/graveyard522-enemies','build/graveyard542-late')
s=s.replace("cmd=r['command'].copy()", "cmd=r['command'].copy();cmd[0]=str(ROOT/'build/graveyard536/player.exe')\nused=int(re.search(r'tape_words_used=(\\d+)',(reference.parent/'run.log').read_text()).group(1))\nsource=Path(cmd[cmd.index('--input-polled')+1]);suffix=out/'after15000.polled.tape';suffix.write_bytes(source.read_bytes()[used*2:]);cmd[cmd.index('--input-polled')+1]=str(suffix);cmd[cmd.index('--load')+1]=str(reference.parent/'enemies.state');cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard529-helper/sprites.assets')")
s=s.replace("i=cmd.index('--wav');del cmd[i:i+2];i=cmd.index('--wav-seconds');del cmd[i:i+2]", '')
s=s.replace("'14250'", "'17800'")
s=s.replace("(out/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())", "(out/'resources.ini').write_text((reference.parent/'resources.ini').read_text()+'graphics.sprites.enemies.vultures = md\\ngraphics.sprites.bones.palette = md\\n')")
s=s.replace('paths=[Path(__file__),reference,', "paths=[Path(__file__),template,source,ROOT/'build/graveyard536/build-report.json',reference,")
exec(compile(s,str(template),'exec'))
