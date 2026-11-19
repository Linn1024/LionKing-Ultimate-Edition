"""Bind bounded ledge/hurt evidence without claiming first-level completion."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_preview_history import bound


def main():
    reports={
        'first_ledge':ROOT/'build/pride-ledge-physics/comparison/report.json',
        'playable_opposite':ROOT/'build/pride-ledge-controlled/playable-comparison/report.json',
        'pad_read_observer':ROOT/'build/pride-ledge-controlled/poll-observer/report.json',
        'original_hurt_selection':ROOT/'build/pride-ledge-controlled/hurt-selection3/report.json',
    }
    expected={
        'first_ledge':('BOUNDED_LEDGE_PROTOCOLS_AUDITED',34),
        'playable_opposite':('BOUNDED_PLAYABLE_OPPOSITE_LEDGE_AUDITED',53),
        'pad_read_observer':('PASS',45),
        'original_hurt_selection':('BOUNDED_ORIGINAL_HURT_SELECTION_AUDITED',504),
    }
    children=[ROOT/f'build/pride-ledge-physics/{s}/report.json' for s in ('snes','md')]
    children += [ROOT/f'build/pride-ledge-controlled/playable-opposite/{s}/report.json' for s in ('snes','md')]
    children += [ROOT/'build/pride-ledge-controlled/find-playable/report.json',
        ROOT/'build/pride-ledge-controlled/opposite/md/report.json',
        ROOT/'build/pride-bounce-owner-work/player/actor-observer/build-report.json',
        ROOT/'build/pride-bounce-owner-work/player/actor-observer2/build-report.json']
    for path in children:bound(path)
    rows={}
    for name,path in reports.items():
        report=bound(path);result,count=expected[name]
        assert report['result']==result and len(report['checks'])==count and all(report['checks'].values())
        rows[name]=dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),checks=count,result=result)
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    report=dict(result='PARTIAL',checks=sum(row['checks'] for row in rows.values()),reports=rows,
        playable_ledge_directions_sampled=2,original_hurt_selector_fixtures=168,fatal_selection_differences=36,
        ending_fixture_rejected_for_playable_120_field_comparison=True,
        first_observer_per_field_poll_column_superseded_by_corrected_probe=True,
        rolled_enemy_contact_difference_retained=True,full_death_gameplay_adapter_enabled=False,
        public_player_unchanged_sha256=digest(public),full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),*reports.values(),*children]})
    target=ROOT/'build/pride-ledge-controlled-latest.json'
    assert not target.exists(),'Preserve a previous index before creating a replacement'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],report['checks'],'bounded ledge/hurt checks; full Pride remains open',flush=True)


if __name__=='__main__':main()
