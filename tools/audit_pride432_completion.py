"""Bounded first-level delivery review; reuse retained checks, do not rerun them."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names={
 'archived_allbugs':'pride-menu245-allbugs',
 'native_routes':'pride-menu226-integrated/native75',
 'menu_timing_audio':'pride-menu246-md-timing',
 'menu_pixels':'pride-menu247-md-pixels',
 'menu_outcomes':'pride-menu262-md-routes',
 'prepared_scenes':'pride380',
 'prepared_gameplay':'pride391',
 'resource_tree':'pride401-ui',
 'walkthrough':'pride406-preset-route',
 'window_route':'pride407-preset-window',
 'arena_window':'pride408-boss-window',
 'save_resume':'pride411-save',
 'natural_retry':'pride414-retry',
 'hud_components':'pride421-hud-play',
 'live_hud_ui':'pride423-hud-ui',
 'installed_package':'pride424-publication',
}
records={}
for key,folder in names.items():
    p=ROOT/'build'/folder/'report.json'
    try:
        r=bound(p);checks=r.get('checks',{})
        if isinstance(checks,dict):failed=[k for k,v in checks.items() if v is False]
        else:failed=[]
        records[key]=dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p),result=r.get('result'),failed_checks=failed,checks_count=len(checks),bound=True)
    except Exception as error:
        records[key]=dict(path=p.relative_to(ROOT).as_posix(),bound=False,error=str(error))
    print(key,records[key],flush=True)
manifest=ROOT/'game-data/install.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'))
installed={}
for key,value in m.items():
    if isinstance(value,dict) and 'file' in value and 'sha256' in value:installed[key]=digest(manifest.parent/value['file'])==value['sha256']
for key,value in m['roms'].items():installed['rom/'+key]=digest(manifest.parent/value['file'])==value['sha256']
package=ROOT/'dist/installed-preview418';info=json.loads((package/'package.json').read_text())
installed['published_player']=digest(package/'LionKing.exe')==info['player_sha256']=='57f409d6ea3a4b67d4d4421deb1991c0a578dc31377f8eea7a1fa077760fd69a'
installed['published_audio_backend']=digest(package/'genesis_plus_gx_libretro.dll')==info['backend_sha256']
installed['launcher_selects_published_player']='dist/installed-preview418' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
out=ROOT/'build/pride432-completion-review';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='REVIEWED' if all(r.get('bound') and not r['failed_checks'] for r in records.values()) and all(installed.values()) else 'REVIEW_ITEMS',reports=records,installed=installed,source_sha256={Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__)),manifest.relative_to(ROOT).as_posix():digest(manifest)},scope='Read retained evidence and installed identities; no game runs, new fidelity search, old-save requirement or universal original-MD equivalence claim.'),indent=2)+'\n')
print('installed',installed,flush=True)
