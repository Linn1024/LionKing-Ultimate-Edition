"""Repeat actual difficulty contacts with only the MD attack-timing leaf selected."""
from pathlib import Path
verifier_source=Path(__file__).with_name('capture_pride_porcupine186_polled.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-porcupine186-polled'","ROOT/'build/pride-porcupine191-md-timing'")
old="(folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)"
new="text=Path(cmd[cmd.index(flag)+1]).read_text()\n        if flag=='--resource-profile':text+='\\ngameplay.levels.pride_lands.porcupine_attack = md\\n'\n        (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)"
assert source.count(old)==1;source=source.replace(old,new)
old="env=dict(clean,TLK_DAMAGE184=str(folder/'damage.csv'),TLK_DAMAGE_FIRST184=str(start+1))"
new=old+"\n    env['TLK_PORCUPINE_ATTACK_TRACE']=str(folder/'attack.csv')"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
source=source.replace("scope='Fresh ordinary Options boots", "scope='Only porcupine attack timing selected MD; all other choices SNES. Fresh ordinary Options boots")
exec(compile(source,str(verifier_source),'exec'))
