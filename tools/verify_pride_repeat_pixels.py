"""Independently reconstruct first and second revival art/palette/mask output."""
import concurrent.futures
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_repeat import BASE
from verify_pride_handoff_default_pixels import verify_default_pixels


def one(item):
    host,name,n=item;root=BASE/('scoped-'+host)/name;r=json.loads((root/'report.json').read_text())
    scene=r['scenes'][n];folder=root if n==0 else root/scene['folder']
    out=verify_default_pixels(folder,r['width'],r['graphics'] in ('frames','all'),r['graphics'] in ('palette','all'),scene['release_age']+1)
    return dict(host=host,case=name,scene=n+1,report_sha256=digest(root/'report.json'),**out)


def main():
    jobs=[('headless',name,n) for name in ('snes-256-native-aot','md-320-all-aot','snes-320-frames-aot','snes-320-palette-lle') for n in (0,1)]
    jobs += [( 'windows',name,n) for name in ('snes-256-native-aot','md-320-all-lle') for n in (0,1)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:cases=list(pool.map(one,jobs))
    paths=[Path(__file__),ROOT/'tools/verify_pride_handoff_default_pixels.py',ROOT/'tools/probe_pride_scene_render.py',
        ROOT/'build/pride-death-controller/original-palettes.csv',ROOT/'build/pride-death-controller/original-fields.csv',
        ROOT/'build/pride-revival-scene/original-revival.csv',ROOT/'build/pride-owned-death-art/original-bitmaps.bin',
        ROOT/'build/pride-owned-revival-art/original-bitmaps.bin',ROOT/'Lion King, The (World).md']
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths}
    out=dict(result='PASS',cases=cases,pixels_compared=sum(r['pixels_compared'] for r in cases),source_sha256=sources)
    (BASE/'pixels-report.json').write_text(json.dumps(out,indent=2)+'\n');print('Twelve first/second scene reconstructions PASS',out['pixels_compared'],'pixels',flush=True)


if __name__=='__main__':main()
