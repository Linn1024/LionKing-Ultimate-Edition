"""Current timeline with owned backend DLL and plain preprocessed C helpers."""
from pathlib import Path
verifier_source=Path(__file__).with_name('observe_pride_battle_music111.py')
source=verifier_source.read_text().replace('pride-battle-music111','pride-battle-music112')
source='\n'.join(line for line in source.splitlines() if not line.lstrip().startswith(('#define BW','#define BP','#undef BW','#undef BP')))+'\n'
source=source.replace('BW(', 'BattleWord112(').replace('BP(', 'BattlePointer112(')
anchor="text+='''\n_Bool __wrap_RtlRunFrame";assert source.count(anchor)==1
source=source.replace(anchor,"text+='''\nstatic unsigned BattleWord112(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}\nstatic unsigned BattlePointer112(unsigned at){return BattleWord112(at)|(unsigned)g_ram[at+2]<<16;}\n_Bool __wrap_RtlRunFrame")
anchor="cmd=ref['commands']['native'].copy()";assert source.count(anchor)==1
source=source.replace(anchor,"import shutil\nshutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')\n"+anchor)
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),verifier_source,bp,base/"genesis_plus_gx_libretro.dll",')
exec(compile(source,str(verifier_source),'exec'))
