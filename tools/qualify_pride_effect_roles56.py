"""Classify every observed Pride static-map miss by its existing semantic owner."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-effect-observer56';out=base/'role-qualification';out.mkdir()
    source=base/'verification/report.json';prior=bound(source);assert prior['result']=='PASS'
    windows=base/'public-windows/report.json';assert bound(windows)['result']=='PASS'
    rompath=ROOT/'Lion King, The (USA).sfc';rom=rompath.read_bytes()
    expected={
        'c00006':dict(hud_role='1',title_role='0',fixed='1',actor_descriptor='c00001',actor_action='000000'),
        'c0d5de':dict(hud_role='0',title_role='0',fixed='1',actor_descriptor='c0d5d9',actor_action='000000'),
        '7e17dd':dict(hud_role='-1',title_role='1',fixed='0',actor_descriptor='c588cb',actor_action='c0679e')}
    checks=dict(original_rom_identity=digest(rompath)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712',
        original_health_hud_callback=rom[1:4]==bytes.fromhex('0102c0'),
        original_roar_hud_callback=rom[0xd5d9:0xd5dc]==bytes.fromhex('a6d6c0'),
        original_opening_caption_callback=rom[0x588cb:0x588ce]==bytes.fromhex('9e67c0'))
    for mode in ('aot','lle'):
        rows=list(csv.DictReader((base/'verification'/mode/'unknown.csv').open()))
        summary=prior['observations'][mode]['summary']
        checks[mode+'_exact_three_nonstatic_pose_keys']=set(r['pose'] for r in rows)==set(expected)
        checks[mode+'_every_row_has_original_owned_procedural_role']=all(
            all(r[key]==value for key,value in expected[r['pose']].items()) for r in rows)
        checks[mode+'_all_95305_pieces_accounted_for']=summary['pieces']==95305 and summary['mapped']==67264 and len(rows)==28041 and summary['pieces']==summary['mapped']+len(rows)
        checks[mode+'_all3418_pride_fields_observed']=summary['frames']==3418
        checks[mode+'_actual_lit_oam_seen_for_each_role']=all(any(r['pose']==pose and int(r['lit_oam_rows'])>0 for r in rows) for pose in expected)
        checks[mode+'_no_world_particle_static_mapping_miss']=not any(r['hud_role']=='-1' and r['title_role']=='0' for r in rows)
        # The existing broader6000-field diagnostic includes a known later-level
        # cub miss. Keep it explicit; never turn scoped Pride coverage into a
        # claim that the subsequent level or all sprites are complete.
        sprites=json.loads((base/'verification'/mode/'sprites.json').read_text())
        checks[mode+'_global_later_pose_report_retained']=sprites['missing_poses']==[0x11372] and not sprites['missing_npc_poses']
    paths=[Path(__file__),source,windows,rompath,ROOT/'engine/runner/tlk_wide.c',ROOT/'engine/runner/tlk_hud_role.h',ROOT/'engine/runner/tlk_title_role.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                classifications={pose:dict(role=('health meter' if pose=='c00006' else 'roar meter' if pose=='c0d5de' else 'dynamic opening-caption glyph producer'),**row) for pose,row in expected.items()},
                no_new_static_sprite_mapping_needed_for_these_entries=True,
                complete_original_renderer_or_all_action_coverage_claimed=False,public_preview_unchanged=True,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
