"""Select the verified arena-revival repair and retain the preceding launcher."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-arena-work';build=bound(base/'build-report.json')
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    binary=base/'tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    components={}
    for name in ('player-check','completion','independence'):
        file=base/name/'report.json';report=bound(file)
        assert report['result']=='PASS' and all(report['checks'].values()),name
        components[name]=dict(report=file.relative_to(ROOT).as_posix(),sha256=digest(file),checks=len(report['checks']))
    launcher=ROOT/'Play Standalone Preview.cmd';original=launcher.read_bytes()
    before=rb'build\pride-title-work\player\native-engine\tlk_pride_player.exe'
    after=rb'build\pride-arena-work\tlk_pride_player.exe'
    assert original.count(before)==1
    archive=base/'launcher-baseline';archive.mkdir()
    old=archive/'Play Standalone Preview.cmd';old.write_bytes(original)
    settings={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'settings/standalone-preview').glob('*.ini')}
    previous=ROOT/'build/pride-title-work/player/native-engine/tlk_pride_player.exe'
    record=dict(original_launcher_sha256=digest(launcher),archived_launcher=old.relative_to(ROOT).as_posix(),
                old_native_player_sha256=digest(previous),existing_settings_sha256=settings)
    (archive/'report.json').write_text(json.dumps(record,indent=2)+'\n')
    launcher.write_bytes(original.replace(before,after))
    assert all(digest(ROOT/name)==sha for name,sha in settings.items())
    result=dict(result='PARTIAL',binary=binary.relative_to(ROOT).as_posix(),binary_sha256=digest(binary),
                components=components,verified_component_checks=sum(r['checks'] for r in components.values()),
                selected_scene_change='Pride Lands hyena-arena nonfinal health death now enters selected MD revival presenter',
                full_first_level_fidelity_complete=False,full_native_cpu_matrix_rerun=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),ROOT/'tools/pride_arena_history.py',base/'build-report.json',launcher,archive/'report.json']})
    (base/'preview-report.json').write_text(json.dumps(result,indent=2)+'\n')
    latest=ROOT/'build/pride-arena-preview-latest.json';assert not latest.exists()
    latest.write_text(json.dumps(result,indent=2)+'\n')
    print('Arena revival preview selected',result['verified_component_checks'],'component checks',flush=True)


if __name__=='__main__':main()
