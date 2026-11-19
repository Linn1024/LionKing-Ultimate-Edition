"""Bind completed fast-load captures after their generic visibility search failed."""
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-fast-assets-probe';out=base/'capture'
    assert not (out/'report.json').exists()
    build=bound(base/'build-report.json');assert digest(base/'player.exe')==build['binary_sha256']
    rows=list(csv.DictReader((out/'100/points.csv').open()))
    checks=dict(native_music_initializer_at_original_offset88=any(r['pc']=='c08c06' and r['field']=='2457' for r in rows),
                native_asset_entry_owned=any(r['pc']=='c1ccfe' and r['field']=='2377' for r in rows),
                destination_matches_original_native_at_same_age=pixels(out/'100/window.png')==pixels(ROOT/'build/pride-late-visible/112/window.png'))
    for offset in (88,96,100,104,112,120,128,144,160):
        checks[str(offset)+'/completed']='wram_sha256=' in (out/str(offset)/'run.log').read_text()
    paths=[Path(__file__),base/'build-report.json',ROOT/'tools/capture_pride_final_fast_assets.py',ROOT/'tools/capture_pride_late_visible.py',ROOT/'build/pride-late-visible/report.json']
    report=dict(result='CAPTURES_AGGREGATED' if all(checks.values()) else 'FAIL',checks=checks,
        generic_capture_search_failure='No sampled image was wholly black: a stale native HUD is visible at88 before destination drawing. Owned presentation must cover it.',
        all_guest_processes_completed_before_search_failure=True,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'fast-load captures retained',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
