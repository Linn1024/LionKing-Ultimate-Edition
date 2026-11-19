"""Research health capped at1 until first death; original fatal-hit logic unchanged."""
from pathlib import Path
p=Path(__file__).with_name('build_hakuna835_observer.py');s=p.read_text().replace('build/hakuna835-observer','build/hakuna841-health')
anchor='    static FILE *audit;static unsigned last_health'
s=s.replace(anchor,'    static int done;if(!done){if(!word(0x2004))done=1;else if(word(0x2004)>1){g_ram[0x2004]=1;g_ram[0x2005]=0;}}\n'+anchor)
exec(compile(s,str(p),'exec'))
