"""Exercise the real launch-sound preview launcher and preserve existing settings."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_player_launcher.py')
source=original_verifier.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-bounce-owner-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_bounce_owner_preview_history import bound')
needle='    snapshots = []';assert source.count(needle)==1
source=source.replace(needle,"""    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    checks['new_player_target']=r'build\\pride-lizard-launch-work\\player\\native-engine\\tlk_pride_player.exe' in launcher.read_text()
    checks['preceding_lizard_player_preserved']=digest(ROOT/'build/pride-lizard-launch-work/player/player.exe')==archive['old_player_sha256'] and digest(ROOT/'build/pride-lizard-launch-work/player/native-engine/tlk_pride_player.exe')==archive['old_native_player_sha256']
    checks['old_launcher_archived']=digest(ROOT/archive['archived_launcher'])==archive['original_launcher_sha256']
    checks['setup_cache_loaded']='resource_cache=loaded' in text
    checks['existing_settings_and_saves_unchanged']=all(digest(ROOT/name)==sha for name,sha in archive['existing_settings_sha256'].items())
"""+needle)
source=source.replace('paths = [Path(__file__), launcher,',
    "paths = [Path(__file__), original_verifier, ROOT/'tools/pride_bounce_owner_preview_history.py', ROOT/'tools/pride_arrival_history.py', archive_path, launcher,")
exec(compile(source,str(original_verifier),'exec'))
