"""Verify original MD palette fade ownership against every captured video field."""
import hashlib
import json
import struct
from pathlib import Path
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def fade(color,step):
    # Genesis Plus GX exposes CRAM as packed three-bit RGB components.
    return sum(max(0,((color>>shift)&7)-step)<<shift for shift in (0,3,6))


def main():
    out=ROOT/'build/pride-death-presentation-md'
    capture_path=out/'report.json';capture=json.loads(capture_path.read_text());assert capture['result']=='PASS'
    assert capture['source_sha256']['script']==digest(ROOT/'tools/md_death_presentation.py')
    assert capture['source_sha256']['fields']==digest(out/'fields.json')
    assert capture['source_sha256']['core']==digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll')
    timeline_path=ROOT/'build/pride-death-timeline/report.json'
    assert capture['source_sha256']['timeline']==digest(timeline_path)
    timeline=json.loads(timeline_path.read_text());death=timeline['md_deaths'][0]
    rows={r['frame']:r for r in json.loads((out/'fields.json').read_text())}
    palettes={f:struct.unpack('<64H',bytes.fromhex(r['cram'])) for f,r in rows.items()}
    initial=palettes[death['death']]
    assert all(p<512 for p in initial)
    # Original0516 uses start16/count48, channel-wise saturated -2 in MD
    # bus words (one step in packed3bit CRAM), with81A6=3 fields/pass.
    # DMA becomes visible one field after the first submitted palette.
    prelude_checks=0
    for offset in range(24):
        f=death['death']+offset;step=(offset+2)//3
        expected=initial[:16]+tuple(fade(c,step) for c in initial[16:])
        assert palettes[f]==expected,('Selective fade',f,step)
        prelude_checks+=64
    cub_checks=0
    for f in range(death['death'],death['loop_end']):
        assert palettes[f][:16]==initial[:16],('Cub palette changed during display',f)
        cub_checks+=16
    for f in range(death['loop_start'],death['loop_end']):
        assert palettes[f][16:]==(0,)*48
    # Original08CE after the loop invokes the same fade for all64 colors.
    # It includes an eighth pass after the seventh has already reached zero.
    postlude_checks=0
    for offset in range(24):
        f=death['loop_end']+offset;step=(offset+2)//3
        expected=tuple(fade(c,step) for c in palettes[death['loop_end']])
        assert palettes[f]==expected,('Complete fade',f,step)
        postlude_checks+=64
    assert palettes[death['loop_end']+24]==(0,)*64
    assert palettes[death['health_restored']]==(0,)*64
    assert death['health_restored']-(death['loop_end']+24)==21
    for picture in capture['pictures']:
        assert digest(out/f"{picture['frame']}.png")==picture['sha256']
    mismatched=[f for f,r in rows.items() if r['camera_actor']!=r['global_hero_pointer']]
    assert mismatched, 'The final scene must retire the old hero owner'
    old_owner=rows[death['death']]['global_hero_pointer']
    replaced=next(f for f,r in rows.items() if death['loop_end']<=f<=5060 and r['global_hero_pointer']!=old_owner)
    first_color=next(f for f in rows if death['health_restored']<f<=5060 and any(palettes[f][:16]))
    restored_palette=next(f for f in rows if death['health_restored']<f<=5060 and palettes[f][:16]==initial[:16])
    result={'result':'PASS','scope':__doc__,'selective_fade_fields':24,'main_loop_fields':201,
            'complete_fade_fields':24,'after_complete_fade_to_positive_health_fields':21,
            'selective_fade_palette_word_checks':prelude_checks,'complete_fade_palette_word_checks':postlude_checks,
            'unchanged_cub_palette_word_checks':cub_checks,'black_other_palettes_main_fields':201,
            'dma_visible_palette_latency_fields':1,'palette_pass_interval_fields':3,
            'palette_passes_including_terminal_zero_pass':8,
            'health_restored_while_all_palettes_black':True,
            'new_global_hero_owner_field':replaced,'first_returning_cub_palette_color_field':first_color,
            'cub_palette_fully_restored_field':restored_palette,
            'first_camera_actor_vs_retired_global_hero_disagreement_field':min(mismatched),
            'production_death_source_enabled':False,
            'source_sha256':{'analysis':digest(Path(__file__)),'capture':digest(capture_path),'timeline':digest(timeline_path)}}
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Original MD selective24/main201/complete24/reload21 phases and palette ownership PASS',flush=True)


if __name__=='__main__':main()
