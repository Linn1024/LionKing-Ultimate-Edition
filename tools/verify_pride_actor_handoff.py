"""Verify input-driven scene release against ordinary presentation and neutral history.

This is a scoped private-host audit, not a first-level completion certificate.
"""
import argparse
import concurrent.futures
import csv
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from run_pride_actor_handoff_matrix import BASE, CONTEXTS
from verify_windows import pixels
from verify_pride_audio_state import wav_data
from verify_pride_handoff_default_pixels import verify_default_pixels


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def bound(folder):
    path=folder/'report.json'
    r=json.loads(path.read_text())
    assert r['exit_code']==0 and len(r['guest'])==2,folder
    assert not r['loaded_states'] and not r['guest_fixture_edits'],folder
    for name,sha in r['source_sha256'].items():
        assert digest(ROOT/name)==sha,(folder,name)
    for name,sha in r['artifacts_sha256'].items():
        assert digest(folder/name)==sha,(folder,name)
    binary=BASE/('actor-handoff-sdl.exe' if r['host']=='sdl' else 'actor-handoff-probe.exe')
    assert digest(binary)==r['binary_sha256'],folder
    return r


def release(folder,ready_age):
    fields=rows(folder/'render-fields.csv')
    last=fields[-1]
    assert last['released']=='1' and last['native_pixel_mismatch']=='0',folder
    assert ready_age<=int(last['age'])<=ready_age+8,(folder,last)
    normals=rows(folder/'normal-owner.csv') if (folder/'normal-owner.csv').exists() else []
    high=[r for r in fields if int(r['pose'],16)&0x80000000]
    indexed={(int(r['field']),int(r['age'])):r for r in normals}
    for r in high:
        n=indexed[int(r['field']),int(r['age'])]
        assert n['normal_started']==n['normal_actor']=='1',n
        delta=(int(n['visible_latch'])-int(n['begin_latch']))&0xffffffff
        assert 0<delta<0x80000000 and int(r['age'])>ready_age,n
        assert int(r['pose'],16)&0xffffff==int(n['native_pose'],16)==int(r['native_cub_pose'],16),r
        assert r['actor_pixels']=='0' and n['native_pieces']==r['native_pieces'],r
    assert len(high)==len(normals),(folder,len(high),len(normals))
    return dict(age=int(last['age']),field=int(last['field']),normal_actor_fields=len(high),
                normal_poses=sorted({r['native_pose'] for r in normals}))


def composed(path):
    """Read actual displayed RGB; high-bit actor records already include the actor."""
    with path.open('rb') as f:
        assert f.read(8)==b'PRDRGB01'
        width,height=struct.unpack('<II',f.read(8));count=width*height
        while header:=f.read(24):
            age,pose,x,y,flip,md=struct.unpack('<IIiiII',header)
            assert len(f.read(32+count*8))==32+count*8
            output=f.read(count*4);assert len(output)==count*4
            yield age,output


def verify_active(folder):
    r=bound(folder)
    context=next(c for c in CONTEXTS if folder.name.startswith(c+'-'))
    ready_age=345 if context=='snes-checkpoint' else 300
    result=dict(case=folder.name,report_sha256=digest(folder/'report.json'))
    if r['presenter']=='owned':
        result['release']=release(folder,ready_age)
        control=folder.parent/f"{context}-{r['width']}-{r['graphics']}-aot-native"
        cr=json.loads((control/'report.json').read_text())
        assert r['guest']==cr['guest'],(folder,'guest versus ordinary')
        assert digest(folder/'route.ram')==digest(control/'route.ram'),(folder,'tracked RAM')
        assert pixels(folder/'picture.png')==pixels(control/'picture.png'),(folder,'final pixels')
        if context!='md-polled':
            previous=ROOT/'build/pride-spawn-revival'/('checkpoint' if context=='snes-checkpoint' else 'default')
            previous_graphics=r['graphics']
            if context=='snes-checkpoint' and previous_graphics in ('frames','palette'):
                # The older checkpoint matrix covered native/all; graphics do not
                # modify this input-prefix guest RAM, also checked against controls.
                previous_graphics='native'
            previous/=f"{r['start_source']}-{r['width']}-{previous_graphics}-{r['execution']}"
            boundary=CONTEXTS[context][3]
            def prefix(path):
                return [line for line in path.read_text().splitlines() if int(line.split()[0])<boundary]
            assert prefix(folder/'route.ram')==prefix(previous/'route.ram'),(folder,'unchanged pre-input tracked RAM')
        if r['execution']=='lle':
            other=folder.parent/f"{context}-{r['width']}-{r['graphics']}-aot-owned"
            for name in ('render-owned.rgb','owner-events.csv','normal-owner.csv'):
                a,b=folder/name,other/name
                assert a.exists()==b.exists(),(folder,name)
                if a.exists():assert digest(a)==digest(b),(folder,name)
    return result


def verify_window(folder):
    r=bound(folder)
    context=next(c for c in CONTEXTS if folder.name.startswith(c+'-'))
    result=dict(case=folder.name,report_sha256=digest(folder/'report.json'))
    if r['presenter']=='owned':
        ready_age=345 if context=='snes-checkpoint' else 300
        # A capture at ready+2 may end before release in a future valid profile.
        fields=rows(folder/'render-fields.csv')
        assert int(fields[-1]['age'])<=ready_age+8,folder
        if r['hud_in_place']:
            # Match the headless in-place HUD, not the deliberately different edge HUD.
            other=BASE/'active'/f"{context}-{r['width']}-{r['graphics']}-{r['execution']}-owned"
            head=dict(composed(other/'render-owned.rgb'))
            for age,data in composed(folder/'render-owned.rgb'):
                assert data==head[age],(folder,age)
            result['headless_scene_pixels_equal']=True
        else:
            other=folder.parent/f"{context}-{r['width']}-{r['graphics']}-aot-native-{r['frames']}-edges"
            cr=json.loads((other/'report.json').read_text())
            assert r['guest']==cr['guest'],(folder,'guest')
            assert pixels(folder/'window.png')==pixels(other/'window.png'),(folder,'client')
            assert wav_data(folder/'audio.wav')==wav_data(other/'audio.wav'),(folder,'PCM')
            result['client_pixels']=r['width']*224*4
        if r['execution']=='lle':
            other=folder.parent/folder.name.replace('-lle-','-aot-')
            assert pixels(folder/'window.png')==pixels(other/'window.png'),(folder,'CPU clients')
            assert wav_data(folder/'audio.wav')==wav_data(other/'audio.wav'),(folder,'CPU PCM')
    return result


def verify_neutral(folder):
    r=bound(folder)
    if r['route']=='checkpoint':
        old=ROOT/'build/pride-spawn-revival/checkpoint'/f"snes-{r['width']}-{r['graphics']}-{r['execution']}"
        ready=345
    else:
        old=ROOT/'build/pride-spawn-revival/default'/f"{r['start_source']}-{r['width']}-{r['graphics']}-{r['execution']}"
        ready=300
    previous=json.loads((old/'report.json').read_text())
    assert r['guest']==previous['guest'],(folder,'neutral guest')
    for name in ('route.ram','picture.png','owner-events.csv'):
        assert digest(folder/name)==digest(old/name),(folder,name)
    count=0
    a,b=list(composed(folder/'render-owned.rgb')),list(composed(old/'render-owned.rgb'))
    assert len(a)==len(b),folder
    for first,second in zip(a,b):
        assert first==second,(folder,first[0],second[0])
        count+=r['width']*224
    return dict(case=folder.name,report_sha256=digest(folder/'report.json'),
                composed_pixels_equal=count,release=release(folder,ready))


def verify_art(folder):
    r=json.loads((folder/'report.json').read_text())
    fields=rows(folder/'render-fields.csv')
    count=len({int(f['age']) for f in fields})
    result=verify_default_pixels(folder,r['width'],r['graphics'] in ('frames','cub','all'),
        r['graphics'] in ('palette','cub','all'),count,checkpoint=folder.name.startswith('snes-checkpoint-'))
    return dict(case=folder.name,report_sha256=digest(folder/'report.json'),**result)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=('active','windows','neutral','pixels','aggregate'))
    args=p.parse_args()
    if args.stage=='aggregate':
        build=json.loads((BASE/'build-report.json').read_text())
        for group in ('source_sha256','production_sha256'):
            for name,sha in build[group].items():assert digest(ROOT/name)==sha,name
        for run in build['runs'].values():
            for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        provenance=json.loads((BASE/'inputs/provenance.json').read_text())
        for name,sha in provenance['source_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in provenance['artifacts_sha256'].items():assert digest(BASE/'inputs'/name)==sha,name
        reports={s:json.loads((BASE/(s+'-verification.json')).read_text()) for s in ('active','windows','neutral','pixels')}
        for s,r in reports.items():
            assert r['result']=='PASS'
            for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,name
            for case in r['cases']:
                folder=BASE/('active' if s=='pixels' else s)/case['case']
                assert digest(folder/'report.json')==case['report_sha256'],folder
        out=dict(result='PARTIAL',scope='Completed post-ready normal actor publication and renderer handoff in excluded hosts.',
            reports_sha256={s:digest(BASE/(s+'-verification.json')) for s in reports},
            cases={s:len(r['cases']) for s,r in reports.items()},
            private_handoff_verified=True,public_player_enabled=False,save_lifecycle_verified=False,
            full_first_level_fidelity_complete=False)
        (ROOT/'build/pride-actor-handoff-latest.json').write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2));return
    function={'active':verify_active,'windows':verify_window,'neutral':verify_neutral,'pixels':verify_art}[args.stage]
    folders=sorted(p for p in (BASE/('active' if args.stage=='pixels' else args.stage)).iterdir() if p.is_dir())
    if args.stage=='pixels':folders=[p for p in folders if p.name.endswith('-aot-owned')]
    assert len(folders)=={'active':102,'windows':44,'neutral':10,'pixels':34}[args.stage],len(folders)
    executor=concurrent.futures.ProcessPoolExecutor if args.stage=='pixels' else concurrent.futures.ThreadPoolExecutor
    with executor(max_workers=3) as pool:
        results=list(pool.map(function,folders))
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),ROOT/'tools/run_pride_actor_handoff_matrix.py',ROOT/'tools/verify_windows.py',
        ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_handoff_default_pixels.py',
        ROOT/'tools/probe_pride_scene_render.py',BASE/'build-report.json',BASE/'inputs/provenance.json')}
    if args.stage=='pixels':
        for p in (ROOT/'build/pride-death-controller/original-palettes.csv',
                  ROOT/'build/pride-death-controller/original-fields.csv',
                  ROOT/'build/pride-revival-scene/original-revival.csv',
                  ROOT/'build/pride-owned-death-art/original-bitmaps.bin',
                  ROOT/'build/pride-owned-revival-art/original-bitmaps.bin',
                  ROOT/'Lion King, The (World).md'):
            sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    out=dict(result='PASS',stage=args.stage,cases=results,source_sha256=sources)
    (BASE/(args.stage+'-verification.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(args.stage,len(results),'PASS',flush=True)


if __name__=='__main__':main()
