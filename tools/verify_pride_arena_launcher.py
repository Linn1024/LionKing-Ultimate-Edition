"""Check the actual arena preview launcher, installed cache and user settings."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-arena-work';bp=base/'preview-report.json';build=bound(bp)
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    out=base/'launcher-verification';out.mkdir();launcher=ROOT/'Play Standalone Preview.cmd'
    cmd=[os.environ['COMSPEC'],'/d','/c',str(launcher),'--frames','600','--no-pace','--no-audio','--no-record','--dump-window',str(out/'window.png')]
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    text=(out/'run.log').read_text();hashes=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))
    reference_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    reference=json.loads(reference_path.read_text())['routes']['idle600']['aot']
    previous=ROOT/'build/pride-title-work/player/native-engine/tlk_pride_player.exe'
    checks=dict(batch_exit=result.returncode==0,native_idle_endpoint=hashes==reference,
        md_audio_and_graphics_ready='Pride Lands graphics ready; MD audio ready' in text,
        correct_arena_target=r'build\pride-arena-work\tlk_pride_player.exe' in launcher.read_text(),
        no_forced_practice_start='--practice-level' not in launcher.read_text(),installed_cache_loaded='resource_cache=loaded' in text,
        previous_player_retained=digest(previous)==archive['old_native_player_sha256'],
        launcher_archived=digest(ROOT/archive['archived_launcher'])==archive['original_launcher_sha256'],
        user_settings_unchanged=all(digest(ROOT/name)==sha for name,sha in archive['existing_settings_sha256'].items()),
        selected_binary_unchanged=digest(ROOT/build['binary'])==build['binary_sha256'],
        distribution_unchanged=digest(ROOT/'dist/development-preview/LionKing.exe')==digest(ROOT/'build/pride-launch2/player.exe'))
    paths=[Path(__file__),bp,archive_path,launcher,reference_path]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'actual launcher checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
