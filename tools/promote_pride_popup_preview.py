"""Select the verified popup player after its pending route gate passes."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_popup_history import bound


def main():
    base=ROOT/'build/pride-popup-work'
    component_path=base/'candidate-report.json';component=bound(component_path)
    assert component['verified_component_checks']==208
    binary=ROOT/component['binary'];assert digest(binary)==component['binary_sha256']
    gate_path=base/'native-gates/play-report.json';gate=json.loads(gate_path.read_text())
    assert gate['result']=='PASS' and gate['route_count']==75
    assert gate['binary_sha256']==component['binary_sha256']
    previous_path=ROOT/'build/pride-scene-template-preview-latest.json';previous=bound(previous_path)
    old_binary=ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'
    assert digest(old_binary)==previous['binary_sha256']
    launcher=ROOT/'Play Standalone Preview.cmd';original=launcher.read_bytes()
    assert digest(launcher)==previous['source_sha256']['Play Standalone Preview.cmd']
    before=rb'build\pride-scene-template-work\player\native-engine\tlk_pride_player.exe'
    after=rb'build\pride-popup-work\player\native-engine\tlk_pride_player.exe'
    assert original.count(before)==1
    archive=base/'player/launcher-baseline';archive.mkdir()
    copy=archive/launcher.name;shutil.copy2(launcher,copy)
    settings=ROOT/'settings/standalone-preview';assert settings.is_dir()
    identities={};copies={}
    for path in settings.rglob('*'):
        if not path.is_file():continue
        dest=archive/'settings'/path.relative_to(settings);dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,dest);name=path.relative_to(ROOT).as_posix()
        identities[name]=digest(path);copies[name]=dest.relative_to(ROOT).as_posix()
    paths=[Path(__file__),component_path,gate_path,previous_path,copy,old_binary,
           *(ROOT/name for name in copies.values())]
    record=dict(result='ARCHIVED',original_launcher_sha256=digest(copy),
                archived_launcher=copy.relative_to(ROOT).as_posix(),old_native_player_sha256=digest(old_binary),
                existing_settings_sha256=identities,settings_archive=copies,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (archive/'report.json').write_text(json.dumps(record,indent=2)+'\n')
    helper=ROOT/'tools/pride_popup_preview_history.py';assert not helper.exists()
    source=(ROOT/'tools/pride_popup_history.py').read_text()
    needle="'pride-scene-template-work/player'):"
    assert source.count(needle)==1
    helper.write_text(source.replace(needle,"'pride-scene-template-work/player','pride-popup-work/player'):"))
    launcher.write_bytes(original.replace(before,after))
    assert all(digest(ROOT/name)==sha for name,sha in identities.items())
    print('Popup preview selected; preceding player and',len(identities),'user files preserved',flush=True)


if __name__=='__main__':main()
