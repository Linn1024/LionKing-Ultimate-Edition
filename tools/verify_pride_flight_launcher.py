"""Verify the real launcher now selects the flight player with existing Setup data/settings."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_player_launcher.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-flight-player'")
anchor="    snapshots = []"
assert source.count(anchor)==1
source=source.replace(anchor,"""    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    checks['new_player_target']=r'build\\pride-flight-player\\native-engine\\tlk_pride_player.exe' in launcher.read_text()
    checks['previous_standalone_preserved']=digest(ROOT/'build/pride-player/player.exe')==archive['old_player_sha256']
    checks['old_launcher_archived']=digest(ROOT/archive['archived_launcher'])==archive['original_launcher_sha256']
    checks['setup_cache_loaded']='resource_cache=loaded' in text
"""+anchor)
source=source.replace('paths = [Path(__file__), launcher,', 'paths = [Path(__file__), original, archive_path, launcher,')
exec(compile(source,str(original),'exec'))
