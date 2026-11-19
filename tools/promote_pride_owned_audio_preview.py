"""Switch the local preview after bound gates, retaining prior launcher/settings."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound


def main():
    base=ROOT/'build/pride-bounce-owner-work/player'
    integration=base/'ownership-integration-report.json';r=bound(integration)
    assert r['result']=='PARTIAL' and r['checks']==313
    assert digest(base/'native-engine/tlk_pride_player.exe')==r['binary_sha256']
    previous=ROOT/'build/pride-lizard-launch-preview-latest.json';old=bound(previous)
    launcher=ROOT/'Play Standalone Preview.cmd';original=launcher.read_bytes()
    assert digest(launcher)==old['source_sha256']['Play Standalone Preview.cmd']
    before=rb'build\pride-lizard-launch-work\player\native-engine\tlk_pride_player.exe'
    after=rb'build\pride-bounce-owner-work\player\native-engine\tlk_pride_player.exe'
    assert original.count(before)==1
    archive=base/'launcher-baseline';archive.mkdir()
    copy=archive/launcher.name;shutil.copy2(launcher,copy)
    settings=ROOT/'settings/standalone-preview';assert settings.is_dir()
    identities={};copies={}
    for path in settings.rglob('*'):
        if not path.is_file():continue
        name=path.relative_to(ROOT).as_posix();target=archive/'settings'/path.relative_to(settings)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
        identities[name]=digest(path);copies[name]=target.relative_to(ROOT).as_posix()
    prior=ROOT/'build/pride-lizard-launch-work/player'
    paths=[Path(__file__),integration,previous,copy,prior/'player.exe',prior/'native-engine/tlk_pride_player.exe',
        *(ROOT/name for name in copies.values())]
    report=dict(result='ARCHIVED',original_launcher_sha256=digest(copy),archived_launcher=copy.relative_to(ROOT).as_posix(),
        old_player_sha256=digest(prior/'player.exe'),old_native_player_sha256=digest(prior/'native-engine/tlk_pride_player.exe'),
        existing_settings_sha256=identities,settings_archive=copies,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (archive/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    # The additional exact launcher generation keeps frozen older reports valid.
    helper=ROOT/'tools/pride_bounce_owner_history.py';text=helper.read_text()
    needle="'pride-ledge-work/player','pride-lizard-launch-work/player'):"
    assert text.count(needle)==1
    text=text.replace(needle,"'pride-ledge-work/player','pride-lizard-launch-work/player','pride-bounce-owner-work/player'):")
    destination=ROOT/'tools/pride_bounce_owner_preview_history.py';assert not destination.exists();destination.write_text(text)
    launcher.write_bytes(original.replace(before,after))
    assert all(digest(ROOT/name)==sha for name,sha in identities.items())
    print('Local preview switched; prior player/launcher and',len(identities),'settings/save files retained',flush=True)


if __name__=='__main__':main()
