"""Research-only health1 on first field; native code/controllers otherwise unchanged."""
from pathlib import Path
p=Path(__file__).with_name('build_hakuna835_observer.py');s=p.read_text().replace('build/hakuna835-observer','build/hakuna837-health')
anchor='    static FILE *audit;static unsigned last_health'
s=s.replace(anchor,'    static int applied;if(!applied){g_ram[0x2004]=1;g_ram[0x2005]=0;applied=1;}\n'+anchor)
exec(compile(s,str(p),'exec'))
