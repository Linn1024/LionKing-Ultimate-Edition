"""Bind compiled prepared composition, guest parity and original glyph evidence.

Passing the declared composition is not complete original MD scene fidelity or
proof of selectable player/lifecycle integration.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_compiled_windows import saved_wram
from verify_windows import hashes,pixels


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def logical_frames(path,width):
    size=56+width*224*12;result={}
    with path.open('rb') as f:
        assert f.read(16)==b'PRDRGB01'+struct.pack('<II',width,224)
        while record:=f.read(size):
            assert len(record)==size
            age=struct.unpack_from('<I',record)[0];sha=hashlib.sha256(record).hexdigest()
            if age in result:assert result[age]==sha
            result[age]=sha
    return result


def main():
    base=ROOT/'build/pride-compiled-prepared';reports={}
    def read(name):
        path=base/name;r=json.loads(path.read_text())
        for source,sha in r.get('source_sha256',{}).items():assert digest(ROOT/source)==sha,source
        reports[name]=digest(path);return r
    build=read('build-report.json');assert build['result']=='BUILT'
    for host,run in build['runs'].items():
        assert digest(base/('compiled-prepared-'+host+'.exe'))==run['binary_sha256']
        for source,sha in run['link_inputs_sha256'].items():assert digest(ROOT/source)==sha,source
    for source,sha in build['production_sha256'].items():assert digest(ROOT/source)==sha,source
    previous=ROOT/'build/pride-compiled-revival/sync-full-headless/report.json'
    baseline=json.loads(previous.read_text())
    expected=baseline['runs']['lle']['guest'];reference_ram=previous.parent/'lle/route.ram'
    total_pixels=total_indices=client_pixels=0;releases={}
    def validate(folder,run,binary,execution):
        for name,sha in run['artifacts_sha256'].items():assert digest(folder/name)==sha,str(folder/name)
        assert hashes(folder/'run.log')==expected
        text=(folder/'run.log').read_text(errors='replace')
        counters=re.search(r'pride_compiled_hook_calls=(\d+) callbacks=(\d+)',text);assert counters
        assert int(counters[2])>0 if execution=='aot' else int(counters[1])==0
        if (folder/'capture.json').exists():
            capture=json.loads((folder/'capture.json').read_text())
            assert capture['execution_completed'] and capture['probe_sha256']==binary
            for name,sha in capture['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for width in (256,320):
        for family,profiles in (('headless',('native','all')),('components',('frames','palette'))):
            modes={}
            for execution in ('aot','lle'):
                name=f'{family}-{width}-{execution}';r=read(name+'/report.json');modes[execution]=r
                assert r['probe_sha256']==build['runs']['probe']['binary_sha256'] and r['execution']==execution
                assert r['prepared_objects'] and r['revival_roar_source']=='md' and r['checkpoint_sources']=='both'
                for profile in profiles:
                    key=profile+'-owned';run=r['runs'][key];folder=base/name/key
                    validate(folder,run,r['probe_sha256'],execution)
                    assert digest(folder/'route.ram')==digest(reference_ram)
                    for event in rows(folder/'prepared-objects.csv'):
                        assert int(event['source_age'])==268
                        assert int(event['staged_pieces'])==(25 if int(event['age'])<298 else 0)
                        assert tuple(int(event[k]) for k in ('health_max','roar_max','roar_current'))==(6,24,0)
                    total_pixels+=run['pixels_compared'];releases[f'{width}-{execution}-{profile}']=run['release_age']
                font=read('fonts-'+name+'.json');assert font['result']=='PASS'
                assert font['original_cpu_current_fonts_and_actual_owned_vram_exact']
                total_indices+=sum(c['actual_raster_indices'] for c in font['cases'].values())
            for profile in profiles:
                a=base/f'{family}-{width}-aot'/(profile+'-owned');b=base/f'{family}-{width}-lle'/(profile+'-owned')
                for name in ('route.ram','render-fields.csv','render-owned.rgb','prepared-fonts.bin','prepared-objects.csv','owner-events.csv','restore-events.csv'):
                    assert digest(a/name)==digest(b/name),(profile,width,name)
        windows={}
        for execution in ('aot','lle'):
            name=f'windows-{width}-{execution}';r=read(name+'/report.json');windows[execution]=r
            assert r['result']=='PASS' and r['probe_sha256']==build['runs']['sdl']['binary_sha256']
            for case,run in r['runs'].items():
                folder=base/name/case
                for artifact,sha in run['artifacts_sha256'].items():assert digest(folder/artifact)==sha,str(folder/artifact)
                counters=re.search(r'pride_compiled_hook_calls=(\d+) callbacks=(\d+)',(folder/'run.log').read_text(errors='replace'))
                assert counters and (int(counters[2])>0 if execution=='aot' else int(counters[1])==0)
                phase=case.split('-',1)[1];phase='death' if phase=='display' else phase
                reference=ROOT/f'build/pride-compiled-revival/sync-windows-{width}'/(phase+'-'+execution)/'run.log'
                assert hashes(folder/'run.log')==hashes(reference)
                client_pixels+=run['exact_window_pixels']
            font=read('fonts-'+name+'.json');assert font['result']=='PASS'
            total_indices+=sum(c['actual_raster_indices'] for c in font['cases'].values())
        for case in windows['aot']['runs']:
            a=base/f'windows-{width}-aot'/case;b=base/f'windows-{width}-lle'/case
            assert hashes(a/'run.log')==hashes(b/'run.log')
            assert pixels(a/'window.png')==pixels(b/'window.png')
            ar,offset=saved_wram(a/'snapshot.state',hashes(a/'run.log')['wram_sha256'])
            br,_=saved_wram(b/'snapshot.state',hashes(b/'run.log')['wram_sha256'],offset);assert ar==br
            assert logical_frames(a/'render-owned.rgb',width)==logical_frames(b/'render-owned.rgb',width)
            for name in ('owner-events.csv','restore-events.csv','owner-fields.csv','restore-fields.csv'):
                assert rows(a/name)==rows(b/name),(case,width,name)
            if (a/'prepared-objects.csv').exists() or (b/'prepared-objects.csv').exists():
                assert rows(a/'prepared-objects.csv')==rows(b/'prepared-objects.csv'),(case,width,'prepared-objects.csv')
    pcm={}
    for execution in ('aot','lle'):
        name='audio-320-'+execution;r=read(name+'/report.json')
        assert r['probe_sha256']==build['runs']['sdl']['binary_sha256']
        for case,run in r['runs'].items():
            folder=base/name/case;validate(folder,run,r['probe_sha256'],execution)
            with wave.open(str(folder/'route.wav'),'rb') as wav:
                assert wav.getnframes()==5400*wav.getframerate()*357366//21477272
                pcm[execution+'-'+case]=wav.readframes(wav.getnframes())
    assert len(pcm)==4 and len(set(pcm.values()))==1
    reference=ROOT/'build/pride-compiled-revival/sync-audio/lle/audio.wav'
    with wave.open(str(reference),'rb') as wav:assert next(iter(pcm.values()))==wav.readframes(wav.getnframes())
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,
        source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        compiled_prepared_composition_parity_verified=True,independent_hero_frames_palette_verified=True,
        original_cpu_installed_font_indices=total_indices,independent_art_composed_pixels=total_pixels,
        actual_windows_clients=24,exact_client_pixels=client_pixels,release_ages=releases,
        full_route_pcm_bytes=len(next(iter(pcm.values()))),full_route_pcm_exact_to_controller=True,
        original_md_complete_scene_verified=False,active_scene_lifecycle_verified=False,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-compiled-prepared-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Compiled prepared art/font/window/state/PCM parity verified; full Pride remains PARTIAL',flush=True)


if __name__=='__main__':main()
