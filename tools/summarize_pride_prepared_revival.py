"""Bind owned revival artwork and actual SDL prepared-bank continuation evidence."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_native_bank


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_native_bank.main()
    art_path=ROOT/'build/pride-owned-revival-art/report.json'
    sdl_path=ROOT/'build/pride-native-bank-sdl/report.json'
    art=json.loads(art_path.read_text());sdl=json.loads(sdl_path.read_text())
    assert art['result']==sdl['result']=='PASS'
    for report in (art,sdl):
        assert not report['production_component_enabled']
        for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert art['native_frames']==art['md_frames']==13 and art['indexed_pixels_per_source']==21835
    assert art['source_buffers_detached'] and art['live_wram_not_required']
    assert art['test_sha256']==digest(ROOT/'engine/build-win/tlk_revival_art_test.exe')
    for name,sha in art['logs_sha256'].items():assert digest(art_path.parent/name)==sha,name
    assert sdl['probe_sha256']==digest(ROOT/'engine/build-win/tlk_native_bank_sdl.exe')
    for name,sha in sdl['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for source,runs in sdl['runs'].items():
        assert source in ('native','both') and set(runs)=={'control','prepared','loaded'}
        for mode,run in runs.items():
            assert run['normal_age']==(551 if mode=='control' else 487)
            assert run['last_second_peak']>0 and run['live_dsp_preserved']==(mode!='control')
            for name,sha in run['files_sha256'].items():
                assert digest(sdl_path.parent/(source+'-'+mode)/name)==sha,(source,mode,name)
        assert runs['loaded']['new_process_exact_pcm_suffix']
    assert set(sdl['runs'])=={'native','both'}
    parent_path=ROOT/'build/pride-native-bank-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    result={'result':'PARTIAL','scope':__doc__,'production_sha256':sdl['production_sha256'],
        'owned_revival_pairs':13,'indexed_pixels_per_source':21835,'actual_sdl_cases':6,
        'new_process_exact_sdl_pcm_continuations':2,'production_death_gameplay_enabled':False,
        'native_song_phase_equivalence_verified':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{'script':digest(Path(__file__)),'art_report':digest(art_path),
                         'sdl_report':digest(sdl_path),'retained_gates':digest(parent_path)},
        'remaining':parent['remaining']}
    (ROOT/'build/pride-prepared-revival-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Owned revival pairs and actual SDL bank/PCM continuation verified; complete Pride integration remains PARTIAL',flush=True)


if __name__=='__main__':main()
