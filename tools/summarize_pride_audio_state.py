"""Index matching-source audio continuation evidence; retain full Pride scope."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe'
    paths=('md-audio-checkpoint/report.json','md-backend-source/report.json','imported-audio/report.json','pride-audio-state/report.json',
           'pride-audio-live-state/report.json','pride-state-profiles/report.json',
           'pride-presentation-state/report.json','presentation-schema-compat/report.json',
           'pride-hyena-taunt-state/report.json','pride-hyena-taunt-switch/report.json',
           'pride-audio-verification/report.json','pride-mix-verification/report.json',
           'pride-camera-completion-verified/report.json','next-level-music/report.json',
           'native-route-verification/play-report.json','native-route-verification/allbugs-report.json',
           'setup-verification/report.json')
    reports={}
    for name in paths:
        path=ROOT/'build'/name;row=json.loads(path.read_text())
        assert row['result']=='PASS',name
        assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',name)
        reports[name]={'result':'PASS','sha256':digest(path)}
    path=ROOT/'build/md-taunt-tail-state/report.json';row=json.loads(path.read_text())
    assert row['result']=='PRESERVED' and row['full_mixed_wav_continuation_exact']
    assert path.stat().st_mtime>=player.stat().st_mtime
    reports['md-taunt-tail-state/report.json']={'result':row['result'],'sha256':digest(path)}
    for name,before in (('play-report.json','hyena-taunt-native-before.json'),
                        ('allbugs-report.json','hyena-taunt-allbugs-before.json')):
        current=json.loads((ROOT/'build/native-route-verification'/name).read_text())
        previous=json.loads((ROOT/'build'/before).read_text());assert current['routes']==previous['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/hyena-taunt-allbugs-before.ram').read_bytes()
    manifest=json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256']==digest(player)
    backend=json.loads((ROOT/'.tools/genesis-plus-gx/tlk-build.json').read_text())
    assert backend['dll_sha256']==digest(ROOT/'dist/genesis_plus_gx_libretro.dll')
    assert backend['source_sha256']==digest(ROOT/'dist/source/Genesis-Plus-GX-source.zip')
    report={'result':'PASS','milestone':'Matching-source playing-audio continuation in Pride Lands',
            'player_sha256':digest(player),'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'installed_manifest_matches_player':True,'outer_save_version':4,'legacy_read_versions':[1,2,3],
            'backend':backend,'native_routes':75,'native_allbugs_frames':60648,
            'native_final_hashes_and_tracked_allbugs_rows_unchanged':True,
            'reports':reports,'full_first_level_fidelity_complete':False,
            'remaining':['Other cub/enemy/effect states, damage/death/revival and interruptions',
                         'Unmapped particles/pickup transitions/title resources',
                         'Enemy reactions, spawn/layout/collision/difficulty comparisons',
                         'Adapted 256-camera ordinary completion and the full Pride checklist']}
    path=ROOT/'build/pride-audio-state-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print('Pride audio-save continuation evidence indexed:',path,flush=True)


if __name__=='__main__':main()
