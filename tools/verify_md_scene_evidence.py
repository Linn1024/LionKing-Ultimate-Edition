"""Validate saved, unforced original Elephant Graveyard background observations."""
import argparse,json,collections
from pathlib import Path
from audit_scenes import ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--replay',type=Path,default=ROOT/'build/md-next-levels-replay');args=ap.parse_args()
    rows=json.loads((args.replay/'scene-backgrounds.json').read_text())
    visible=[r for r in rows if r['level']==2 and r['display_enabled'] and r['normal_background_palette_variants']]
    assert len(visible)>=5000,'Insufficient normal-palette visible third-level coverage'
    assert all(r['name_errors']==0 and r['base_tiles_match'] and r['scroll_previous_errors']==0 and r['line_scroll_mode']==3 and r['size_mode']==1 and r['vertical']==0 for r in visible),'Original third-level video differs from the recipe'
    report={'result':'PASS','scope':'Original MD normal-palette visible frames; fades and full-core synchronization remain separate',
            'level':2,'frames':len(visible),'range':[visible[0]['frame'],visible[-1]['frame']],
            'visible_name_checks':sum(r['name_cells'] for r in visible),'name_errors':0,'all_base_tiles_match':True,
            'all_224_line_scrolls_match_previous_camera':True,'camera_x_range':[min(r['camera_x'] for r in visible),max(r['camera_x'] for r in visible)],
            'excluded_initialization_fade_frames':sum(r['level']==2 for r in rows)-len(visible),
            'second_level_background_enabled':False}
    out=ROOT/'build/graveyard-background';out.mkdir(parents=True,exist_ok=True);(out/'original-frame-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original Elephant Graveyard:',len(visible),'visible frames; names, tiles and 224-line previous-camera scroll PASS',flush=True)


if __name__=='__main__':main()
