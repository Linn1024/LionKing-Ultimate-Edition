"""Index the lizard defeat cue and retained regressions without shrinking Pride scope."""
import hashlib
import json
import re
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe'
    runtime=('pride-lizard-defeat/report.json','pride-lizard-defeat-switch/report.json',
             'pride-hyena-taunt-switch/report.json','pride-mix-verification/report.json',
             'pride-camera-completion-verified/report.json','pride-audio-state/report.json',
             'pride-audio-live-state/report.json','imported-audio/report.json',
             'pride-hyena-taunt/report.json','pride-hyena-taunt-state/report.json',
             'pride-presentation-state/report.json','presentation-schema-compat/report.json',
             'setup-verification/report.json','native-route-verification/play-report.json',
             'native-route-verification/allbugs-report.json')
    reports={}
    for name in (*runtime,'lizard-defeat-original/native.json','lizard-defeat-original/md.json','lizard-defeat-original/comparison.json'):
        path=ROOT/'build'/name;row=json.loads(path.read_text());assert row['result']=='PASS',name
        if name in runtime:assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',name)
        reports[name]={'result':'PASS','sha256':digest(path)}
    for name,before in (('play-report.json','lizard-defeat-native-before.json'),
                        ('allbugs-report.json','lizard-defeat-allbugs-before.json')):
        current=json.loads((ROOT/'build/native-route-verification'/name).read_text())
        previous=json.loads((ROOT/'build'/before).read_text());assert current['routes']==previous['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/hyena-taunt-allbugs-before.ram').read_bytes()
    manifest=json.loads((ROOT/'game-data/install.json').read_text());assert manifest['player_sha256']==digest(player)
    raw=(ROOT/'build/lizard-defeat-mx.log').read_bytes();text=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    wrong=len(re.findall(r'^WRONG\b',text,re.M));unproven=len(re.findall(r'^UNPROVEN\b',text,re.M))
    assert wrong==0 and unproven==11
    report={'result':'PASS','scope':__doc__,'resource_id':'audio.effects.world.defeat_puff',
            'player_sha256':digest(player),'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'installed_manifest_matches_player':True,'original_defeats_each_version':2,
            'original_timer_animation_updates_compared':64,'original_md_program':165,
            'native_has_no_separate_defeat_cue':True,'native_guest_writes_by_adapter':False,
            'native_routes':75,'native_allbugs_frames':60648,'native_baselines_unchanged':True,
            'exit_mx':{'wrong':wrong,'existing_unproven':unproven,'full_proof':False},
            'verified_background_levels':manifest['scene_cache']['verified_background_levels'],
            'cache_sha256':manifest['scene_cache']['sha256'],'reports':reports,
            'full_first_level_fidelity_complete':False,
            'remaining':['Defeat and other particle artwork/palettes, pickup transitions and title resources',
                         'Other cub/enemy states and timing, damage/death/revival and interruptions',
                         'Enemy reactions/spawn/layout/collision/difficulty comparisons',
                         'Hyena defeat callback/event semantics and unrelated native event22',
                         'Adapted256 ordinary completion and the full Pride checklist']}
    path=ROOT/'build/pride-lizard-defeat-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD-only lizard defeat and retained baseline evidence indexed:',path,flush=True)


if __name__=='__main__':main()
