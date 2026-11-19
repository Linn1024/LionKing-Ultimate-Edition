"""Explore ordinary controls with current private saves; verify a cold full-WRAM replay."""
from pathlib import Path

original_planner=Path(__file__).with_name('pride_route_planner.py')
source=original_planner.read_text()
source=source.replace("ROOT/'engine/build-win/tlk_headless.exe'", "ROOT/'build/pride-rng-player3/width-observer/player.exe'")
source=source.replace("env=os.environ.copy();env.update(TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(folder))",
    """env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_OBS_DUMP_FIELDS=str(frame),TLK_OBS_DUMP_DIR=str(folder),TLK_TRACKED_RAM_LOG=str(folder/'game.ram'))""")
source=source.replace("'--input-polled',tape,'--ram-log',folder/'game.ram',", "'--input-polled',tape,'--config',config,'--no-pace','--no-audio','--no-record','--wav',folder/'audio.wav','--wav-seconds',120,")
source=source.replace("    base=[host,", "    config=out/'host.ini';config.write_text('opengl = 0\\nscale = 1\\n')\n    base=[host,")
source=source.replace("f'hl_wram_{frame}.bin'", "f'wram-{frame}.bin'")
source=source.replace('f"hl_wram_{best[\'frame\']}.bin"', 'f"wram-{best[\'frame\']}.bin"')
source=source.replace("'scope':__doc__,'headless_sha256':host_hash,",
    "'scope':__doc__,'headless_sha256':host_hash,'source_sha256':{str(p.relative_to(ROOT)).replace('\\\\','/'):digest(p) for p in (Path(__file__),original_planner)},")
exec(compile(source,str(original_planner),'exec'))
