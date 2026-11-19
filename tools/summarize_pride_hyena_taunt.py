"""Index taunt capability evidence and retain the confirmed MD audio-save gap."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe'
    paths=['pride-hyena-taunt/report.json','pride-hyena-taunt-state/report.json',
           'pride-hyena-taunt-switch/report.json','pride-camera-completion-verified/report.json',
           'pride-mix-verification/report.json','native-route-verification/play-report.json',
           'native-route-verification/allbugs-report.json','setup-verification/report.json']
    reports={}
    for name in paths+['hyena-taunt-original/report.json','hyena-taunt-native-original/report.json']:
        path=ROOT/'build'/name;value=json.loads(path.read_text());assert value['result']=='PASS',name
        if name in paths:assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',name)
        reports[name]={'result':'PASS','sha256':digest(path)}
    for name,before in [('play-report.json','hyena-taunt-native-before.json'),
                        ('allbugs-report.json','hyena-taunt-allbugs-before.json')]:
        current=json.loads((ROOT/'build/native-route-verification'/name).read_text())
        previous=json.loads((ROOT/'build'/before).read_text());assert current['routes']==previous['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/hyena-taunt-allbugs-before.ram').read_bytes()
    manifest=json.loads((ROOT/'game-data/install.json').read_text());assert manifest['player_sha256']==digest(player)
    gap_path=ROOT/'build/md-taunt-tail-state/report.json';gap=json.loads(gap_path.read_text())
    assert gap['result'] in ('GAP_CONFIRMED','PRESERVED')
    assert gap['md_tail_preserved']==(gap['result']=='PRESERVED')
    pairs=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
    assert len(pairs)==151 and sum(row['role']=='hyena' for row in pairs)==78
    report={'result':'PASS','scope':'New taunt artwork/entry voice and retained native execution; not full Pride completion',
            'player_sha256':digest(player),'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'installed_manifest_matches_player':True,'cache_version':1,'cache_sha256':manifest['scene_cache']['sha256'],
            'resource_id':'audio.effects.world.hyena_taunt','npc_pairs':151,'hyena_pairs':78,
            'new_taunt_pairs':8,'original_taunt_actions_each_version':2,'fields_per_original_action':34,
            'natural_entry_cues_each_run':2,'first_loaded_fields_compared':4,
            'native_routes':75,'native_allbugs_frames':60648,'native_final_hashes_unchanged':True,
            'native_allbugs_tracked_rows_unchanged':True,'reports':reports,
            'full_first_level_fidelity_complete':False,
            'outstanding_audio_state_audit':{'result':gap['result'],'sha256':digest(gap_path),
                'peaks':gap['md_voice_peaks_after_saved_field'],'md_tail_preserved':gap['md_tail_preserved']},
            'next_required_audio_work':None if gap['md_tail_preserved'] else 'Serialize/restore isolated MD driver, queued commands, resampler/mixer and host audio continuation under matching sources',
            'other_remaining_scope':'Keep the complete Pride checklist: other actor/effect states, transitions, spawn/layout/collision/difficulty, adapted256 route'}
    path=ROOT/'build/pride-hyena-taunt-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print('Taunt evidence and outstanding audio-state gap indexed:',path,flush=True)


if __name__=='__main__':main()
