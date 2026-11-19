"""Reuse only the focused revival/current-save checks for prepared native meters."""
from pathlib import Path
template309=Path(__file__).with_name('verify_pride_revival299_runtime.py')
source=template309.read_text().replace('pride-revival299-runtime','pride-native-hud309-runtime')
source=source.replace("build=ROOT/'build/pride-revival297-installed/build-report.json'","build=ROOT/'build/pride-native-hud307-installed/build-report.json'")
source=source.replace("'build/pride-checkpoint287-installed/player.exe' if version=='old' else 'build/pride-revival297-installed/player.exe'","'build/pride-revival297-installed/player.exe' if version=='old' else 'build/pride-native-hud307-installed/player.exe'")
source=source.replace("cmd=ref['commands']['320-md-snes-3285-new'].copy()","cmd=ref['commands']['320-md-snes-3285-new'].copy();cmd+=['--revival-assets',str(ROOT/'build/pride-revival297-installed/revival.assets')]")
source=source.replace("cmd+=['--revival-assets',str(build.parent/'revival.assets')]","cmd+=['--native-hud-assets',str(build.parent/'native-hud.assets')]")
source=source.replace("cmd.index('--revival-assets')","cmd.index('--native-hud-assets')")
source=source.replace('revival_assets=loaded','native_hud_assets=loaded').replace('installed_revival_loaded','installed_native_hud_loaded')
source=source.replace('Installed revival data is missing or incompatible. Run Setup.','Installed native HUD data is missing or incompatible. Run Setup.')
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template309,reference,')
source=source.replace('against287','against297').replace('prepared image clone staging','prepared native meter copy staging')
exec(compile(source,str(template309),'exec'))
