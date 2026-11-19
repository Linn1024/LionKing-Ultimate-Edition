"""Bind the ceiling milestone to current binaries and its bounded evidence.

This indexes completed component checks. A PARTIAL result deliberately retains
the later controller-route divergence and the unfinished first-level scope.
"""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    head=ROOT/'engine/build-win/tlk_headless.exe'
    player=ROOT/'dist/LionKing.exe'
    def read(relative):
        return json.loads((ROOT/relative).read_text())
    evidence={}
    def index(relative,expected='PASS',fresh=False):
        path=ROOT/relative;report=read(relative)
        assert report['result']==expected,(relative,report['result'])
        if fresh:assert path.stat().st_mtime>=head.stat().st_mtime,relative+' is stale'
        evidence[relative]=digest(path)
        return report
    manifest=read('game-data/install.json')
    assert manifest['player_sha256']==digest(player)
    unit=ROOT/'build/pride-ceiling-unit.log'
    with unit.open('wb') as output:
        subprocess.run([str(ROOT/'engine/build-win/tlk_ceiling_test.exe'),
                        str(ROOT/'Lion King, The (USA).sfc'),str(ROOT/'Lion King, The (World).md')],
                       stdout=output,stderr=subprocess.STDOUT,check=True)
    evidence['build/pride-ceiling-unit.log']=digest(unit)
    index('build/pride-ceiling-original/matrix.json')
    index('build/pride-ceiling-clearance-original/report.json')
    index('build/pride-ceiling-next-gap/contact-gap.json','PARTIAL')
    switch=index('build/pride-ceiling-switch/report.json',fresh=True)
    assert switch['player_sha256']==digest(player)
    states=index('build/pride-state-profiles/report.json',fresh=True)
    assert len(states['matching_source_hashes'])==18 and states['mismatches_rejected_before_load']==30
    index('build/setup-verification/report.json',fresh=True)
    index('build/pride-mix-verification/report.json',fresh=True)
    combinations={}
    for rows,clearance,fields in [('snes','snes',94),('md','snes',101),('snes','md',94),('md','md',466)]:
        folder=(ROOT/'build/pride-ceiling-combined/aot' if rows==clearance=='md'
                else ROOT/f'build/pride-ceiling-controls/{rows}-{clearance}')
        relative=str((folder/'early-audit.json').relative_to(ROOT)).replace('\\','/')
        report=index(relative,'PARTIAL',True)
        assert report['headless_sha256']==digest(head)
        assert report['matched_initial_integer_position_fields']==fields
        assert report['ceiling_row_source']==rows and report['ceiling_clearance_source']==clearance
        observed=list(csv.DictReader((folder/'ceiling.csv').open())) if (folder/'ceiling.csv').exists() else []
        assert {row['kind'] for row in observed}==({'rows'} if rows=='md' else set())|({'clearance'} if clearance=='md' else set())
        combinations[rows+' / '+clearance]={'matching_initial_position_fields':fields,'first_gap':report['first_gap']}
    a=ROOT/'build/pride-ceiling-combined/aot';b=ROOT/'build/pride-ceiling-combined/lle'
    other=index('build/pride-ceiling-combined/lle/early-audit.json','PARTIAL',True)
    assert other['headless_sha256']==digest(head) and other['frames']==5500
    parity={}
    for name in ('native-probe.ram','frame-fnv.log'):
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
        parity[name]=digest(a/name)
    for field in range(1030,1039):
        name=f'hl_wram_{field}.bin'
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
    for before,after in [('build/ceiling-native-before.json','build/native-route-verification/play-report.json'),
                         ('build/ceiling-allbugs-before.json','build/native-route-verification/allbugs-report.json')]:
        report=index(after,fresh=True)
        assert read(before)==report,after+' changed from native baseline'
    native_ram=ROOT/'build/native-route-verification/allbugs-aot.ram'
    assert native_ram.read_bytes()==(ROOT/'build/ceiling-allbugs-before.ram').read_bytes()
    mx=(ROOT/'build/pride-ceiling-exit-mx.log').read_text(encoding='utf-16')
    assert not re.search(r'^WRONG',mx,re.M) and len(re.findall(r'^UNPROVEN',mx,re.M))==11
    report={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(head),
        'installed_player_matches':True,'source_combinations':combinations,'selected_source_mode_parity':parity,
        'native_75_routes_and_60648_allbugs_unchanged':True,'component_evidence_sha256':evidence,
        'first_level_fidelity_complete':False,'derived_md_route_completed':False,
        'next_gap':other['first_gap'],'remaining':'Later behavior/contact differences, interruptions and revival/bonus scope, remaining art/audio/unknown poses, ordinary mixed-source 320/256 completion.'}
    target=ROOT/'build/pride-ceiling-progress-latest.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('Ceiling component evidence indexed; full Pride scope remains PARTIAL',flush=True)


if __name__=='__main__':main()
