"""Compare actual owned raster CHR readback, including zeros, with CPU fonts.

This isolates native font installation from final layering/source HUD choice.
Whole-frame and actual-window checks are separate evidence.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def indices(font):
    result=bytearray()
    for y in range(16):
        for x in range(64):
            at=y//8*256+x//8*32+(y&7)*2;bit=7-(x&7)
            result.append(sum(((font[at+plane//2*16+plane%2]>>bit)&1)<<plane for plane in range(4)))
    return bytes(result)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width',type=int,choices=(256,320),default=320)
    parser.add_argument('--sdl',action='store_true',help='Check installed glyphs in actual window captures')
    parser.add_argument('--capture-root',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--profiles',nargs='+',choices=('native','frames','palette','all'),default=['native','all'])
    args=parser.parse_args()
    partial_root=ROOT/'build/pride-native-hud-current';full_root=ROOT/'build/pride-native-hud-oracle'
    inputs=[Path(__file__),partial_root/'report.json',partial_root/'original-fonts.bin',
            full_root/'report.json',full_root/'original-fonts.bin']
    for root in (partial_root,full_root):
        report=json.loads((root/'report.json').read_text());assert report['result']=='PASS'
        for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in report['artifacts_sha256'].items():assert digest(root/name)==sha,name
    raw=inputs[2].read_bytes();assert raw[:8]==b'SNHUD002'
    fonts={tuple(struct.unpack_from('<5I',raw,offset)[:4]):raw[offset+532:offset+1044]
           for offset in range(8,len(raw),1044)}
    raw=inputs[4].read_bytes();assert raw[:8]==b'SNHUD001'
    full={struct.unpack_from('<2I',raw,offset):raw[offset+520:offset+1032]
          for offset in range(8,len(raw),1032)}
    parent=ROOT/f'build/pride-scene-render-prepared-headless-{args.width}-5400-checkpoint-both-roar-md'
    if args.sdl:parent=ROOT/f'build/pride-scene-prepared-windows-{args.width}-checkpoint-both-roar-md'
    if args.capture_root:parent=ROOT/args.capture_root
    path=parent/'report.json';report=json.loads(path.read_text());inputs.append(path)
    assert report['result']==('PASS' if args.sdl else 'OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN')
    assert report['revival_roar_source']=='md' and report['prepared_objects']
    for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    cases={};cache={}
    names=[p+'-'+phase for p in args.profiles for phase in (('revival','ready') if args.sdl else ('owned',))]
    for name in names:
        folder=parent/name;run=report['runs'][name]
        last_age=run['controller_age'] if args.sdl else run['release_age']
        for artifact_name,sha in run['artifacts_sha256'].items():assert digest(folder/artifact_name)==sha,artifact_name
        path=folder/'prepared-fonts.bin';inputs.append(path)
        raw=path.read_bytes();assert raw[:8]==b'PRDHUD01' and (len(raw)-8)%1052==0
        events_path=folder/'prepared-objects.csv';owner_path=folder/'owner-events.csv'
        inputs.extend((events_path,owner_path))
        events=list(csv.DictReader(events_path.open()))
        starts=[r for r in csv.DictReader(owner_path.open()) if r['event']=='begin']
        assert len(starts)==1
        start=int(starts[0]['field'])
        assert (len(raw)-8)//1052==len(events)*2
        compared=zeros=0;seen=set()
        for n,offset in enumerate(range(8,len(raw),1052)):
            age,kind,maximum,current,initial,x,y=struct.unpack_from('<7I',raw,offset)
            event=events[n//2];display_age=int(event['field'])-start
            assert kind==(1 if n%2==0 else 0) and age==int(event['age'])==min(display_age,345)
            assert 270<=display_age<=last_age and y==14
            if kind==0:
                assert maximum==24 and current==0 and x==16
                key=(kind,maximum,current,initial)
                if key not in cache:cache[key]=indices(fonts[key])
                expected=cache[key]
            else:
                assert kind==1 and maximum==current==6 and x==200
                key=(kind,maximum)
                if key not in cache:cache[key]=indices(full[key])
                expected=cache[key]
            actual=raw[offset+28:offset+1052]
            assert actual==expected,(name,age,kind,initial)
            compared+=len(actual);zeros+=actual.count(0);seen.add((display_age,kind))
        assert seen=={(age,kind) for age in range(270,last_age+1) for kind in (0,1)}
        cases[name]=dict(actual_raster_indices=compared,transparent_indices=zeros,
                            first_age=270,last_age=last_age)
    assert set(cases)==set(names)
    result=dict(result='PASS',scope=__doc__,width=args.width,cases=cases,
        original_cpu_current_fonts_and_actual_owned_vram_exact=True,
        source_palette_or_final_layering_verified=False,actual_windows_captured=args.sdl,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in inputs})
    out=ROOT/f'build/pride-checkpoint-player/empty-roar-fonts-{"sdl-" if args.sdl else ""}{args.width}.json'
    if args.output:out=ROOT/args.output
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('Owned'+str(args.width)+' raster glyphs, including transparent indices, match original CPU current-value fonts: '+str(cases),flush=True)


if __name__=='__main__':main()
