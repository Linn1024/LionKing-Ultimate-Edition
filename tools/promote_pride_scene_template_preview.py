"""Promote only after full repair gates; preserve preceding launcher/user data."""
import json
from pathlib import Path
import shutil
import pride_scene_template_history as history
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-scene-template-work/player'
    integration=base/'integration175-report.json';report=history.bound(integration)
    assert report['result']=='PARTIAL' and report['checks']==175
    assert report['native75_complete'] and report['allbugs_complete']
    assert {'supported_mixture_completion','preceding_public_completion'}<=set(report['reports'])
    assert digest(base/'native-engine/tlk_pride_player.exe')==report['binary_sha256']
    previous=ROOT/'build/pride-bounce-owner-preview-latest.json';old=history.bound(previous)
    launcher=ROOT/'Play Standalone Preview.cmd';original=launcher.read_bytes()
    assert digest(launcher)==old['source_sha256']['Play Standalone Preview.cmd']
    before=rb'build\pride-bounce-owner-work\player\native-engine\tlk_pride_player.exe'
    after=rb'build\pride-scene-template-work\player\native-engine\tlk_pride_player.exe'
    assert original.count(before)==1
    archive=base/'launcher-baseline';archive.mkdir()
    copy=archive/launcher.name;shutil.copy2(launcher,copy)
    settings=ROOT/'settings/standalone-preview';assert settings.is_dir()
    identities={};copies={}
    for path in settings.rglob('*'):
        if not path.is_file():continue
        target=archive/'settings'/path.relative_to(settings);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target);name=path.relative_to(ROOT).as_posix()
        identities[name]=digest(path);copies[name]=target.relative_to(ROOT).as_posix()
    prior=ROOT/'build/pride-bounce-owner-work/player'
    paths=[Path(__file__),integration,previous,copy,prior/'player.exe',prior/'native-engine/tlk_pride_player.exe',*(ROOT/name for name in copies.values())]
    record=dict(result='ARCHIVED',original_launcher_sha256=digest(copy),archived_launcher=copy.relative_to(ROOT).as_posix(),
        old_player_sha256=digest(prior/'player.exe'),old_native_player_sha256=digest(prior/'native-engine/tlk_pride_player.exe'),
        existing_settings_sha256=identities,settings_archive=copies,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (archive/'report.json').write_text(json.dumps(record,indent=2)+'\n')
    text=history.source
    needle="'pride-ledge-work/player','pride-lizard-launch-work/player','pride-bounce-owner-work/player'):"
    assert text.count(needle)==1
    text=text.replace(needle,"'pride-ledge-work/player','pride-lizard-launch-work/player','pride-bounce-owner-work/player','pride-scene-template-work/player'):")
    helper=ROOT/'tools/pride_scene_template_preview_history.py';assert not helper.exists();helper.write_text(text)
    launcher.write_bytes(original.replace(before,after))
    assert all(digest(ROOT/name)==sha for name,sha in identities.items())
    print('Repair preview selected; preceding player and',len(identities),'settings/save files preserved',flush=True)


if __name__=='__main__':main()
