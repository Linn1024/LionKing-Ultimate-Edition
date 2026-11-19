"""Bind menu cue meanings to original code, ordinary controls and reviewed pictures."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    names=['pride-audio-scene76','pride-title-audio77','pride-title-native77','pride-menu-audio78','pride-menu-protocol79']
    reports={};checks={};paths=[Path(__file__)]
    for name in names:
        path=ROOT/'build'/name/'report.json';r=bound(path);paths.append(path);reports[name]=r
        checks[name+'_bound']=all(r['checks'].values())
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native_rows=[('title_cursor',5,0xc46849,100),('title_cursor',5,0xc468a2,100),
                 ('title_selection',6,0xc467cf,101),('title_selection',6,0xc46804,101),
                 ('options_adjustment',6,0xc46a56,101),('options_exit',5,0xc469db,0)]
    for leaf,event,caller,value in native_rows:
        checks[f'native_{caller:06x}_exact_parameter_call']=snes[(caller&0x3fffff)-10:caller&0x3fffff]==bytes.fromhex('f40000f4')+bytes([event,0])+bytes.fromhex('22ec2cc2')
    for address,value in [(0x295678,100),(0x2952ea,101),(0x294f62,101)]:
        checks[f'md_{address:06x}_exact_fm_dispatch']=md[address:address+12]==bytes.fromhex('303c')+value.to_bytes(2,'big')+bytes.fromhex('7e024eb9002d0000')
    protocol=reports['pride-menu-protocol79'];options=protocol['observations']['options']['calls']
    fx=[(int(r['frame']),int(r['selector']),int(r['value'])) for r in options if r['selector'] in ('2','19')]
    checks['ordinary_options_six_expected_effect_calls']=fx==[(990,2,100),(1010,2,101),(1080,2,101),(1110,2,101),(1140,2,100),(1170,2,100)]
    checks['ordinary_start_confirmation101']=any(r['frame']=='990' and r['selector']=='2' and r['value']=='101' for r in protocol['observations']['start']['calls'])
    checks['ordinary_options_return1200_no_separate_effect']=not any(1200<=field<=1220 for field,_,_ in fx)
    neutral=reports['pride-title-audio77']['observations']['neutral']['calls']
    checks['neutral_title_has_no_separate_fm_or_pcm_effect_before1400']=not any(r['selector'] in ('2','19') for r in neutral)
    paths += [ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md']
    out=ROOT/'build/pride-menu-audio80-originals';out.mkdir()
    report=dict(result='MENU_CUE_MEANINGS_VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,
                resource_calls=[dict(resource='audio.effects.'+leaf,native_event=event,native_caller=f'{caller:06x}',md_fm=value) for leaf,event,caller,value in native_rows],
                native600_630_730_and_md_title_options_pictures_visually_reviewed=True,
                finding='Former opening-card effects are ordinary menu navigation/selection/adjustment/return calls, not introductory voices.',
                limitation='Originals use distinct routes and display timing. No whole menu, Options cursor, sound-test, title music or full first-level equivalence claim.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
