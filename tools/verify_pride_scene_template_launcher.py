"""Exercise the actual repair launcher, imported ROM/cache and retained settings."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_player_launcher.py')
source=original.read_text()
changes={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-scene-template-work/player'",
    'from summarize_pride_practice import bound':'from pride_scene_template_preview_history import bound',
    '    snapshots = []':"""    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    checks['repair_player_target']=r'build\\pride-scene-template-work\\player\\native-engine\\tlk_pride_player.exe' in launcher.read_text()
    checks['preceding_ownership_player_preserved']=digest(ROOT/'build/pride-bounce-owner-work/player/player.exe')==archive['old_player_sha256'] and digest(ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe')==archive['old_native_player_sha256']
    checks['old_launcher_archived']=digest(ROOT/archive['archived_launcher'])==archive['original_launcher_sha256']
    checks['setup_cache_loaded']='resource_cache=loaded' in text
    checks['existing_settings_and_saves_unchanged']=all(digest(ROOT/name)==sha for name,sha in archive['existing_settings_sha256'].items())
    snapshots = []""",
    'paths = [Path(__file__), launcher,':
        "paths = [Path(__file__), original,ROOT/'tools/pride_scene_template_preview_history.py',archive_path,launcher,",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
