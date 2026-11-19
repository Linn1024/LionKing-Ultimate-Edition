"""Verify installed native payloads preserve actual Windows final-life behavior."""
import csv
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-title-native14');parser.add_argument('--output',default='continue-regressions');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    prior=ROOT/'build/pride-final-menu-player10'
    sources=[prior/'layout/report.json',prior/'handoff/report.json'];old=[bound(p) for p in sources]
    prepared=ROOT/'build/pride-title-native-installed/setup-verification/Game data & native loads';manifest=prepared/'install.json';info=json.loads(manifest.read_text())
    native=prepared/info['native_final_assets']['file'];menu=prepared/info['menu_assets']['file']
    out=base/args.output;out.mkdir();checks={};commands={};environments={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    bank=ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'
    env=dict(clean,TLK_FINAL_MD_ART='1',TLK_CONTINUE_BANK_RECORD=str(bank))
    def run(width,kind,age,label=None,load=None,save=False,enabled=True,lle=False,asset=native,trace=False):
        name=f'{width}-{kind}-{label or age}';folder=out/name;folder.mkdir()
        template=old[0]['commands'][f'{width}-{kind}-{197 if kind=="yes" else 160}']
        cmd=template.copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:
            at=cmd.index('--save-at');del cmd[at:at+3]
        for flag,value in [('--resource-profile',out/f'{width}.ini'),('--config',out/'host.ini'),('--frames',3894+age),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav'),('--final-menu-assets',menu)]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        if asset is not None:cmd+=['--final-native-assets',str(asset)]
        actual=env.copy()
        if not enabled:actual.pop('TLK_FINAL_MD_ART')
        if trace:actual['TLK_CONTINUE_EXIT_LOG']=str(folder/'exit.csv')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[name]=cmd;environments[name]={k:v for k,v in actual.items() if k.startswith('TLK_')}
        print(name,'exit',result.returncode,flush=True);return folder,result.returncode
    for width in (256,320):
        (out/f'{width}.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        frames={}
        for kind,age in [('neutral',140),('neutral',160),('no',150),('no',151),('yes',124),('yes',182),('yes',183),('yes',197),('yes',333),('yes',350),('yes',426),('yes',600)]:
            folder,code=run(width,kind,age,save=(kind,age) in [('neutral',140),('no',150),('yes',182),('yes',333),('yes',600)],trace=kind=='yes' and age==600)
            frames[kind,age]=folder;checks[f'{width}_{kind}{age}_exit']=code==0
            if kind=='yes' and age in (426,600):reference=prior/'handoff'/f'{width}-{"full" if age==426 else "live"}'
            else:reference=prior/'layout'/f'{width}-{kind}-{age}'
            checks[f'{width}_{kind}{age}_picture']=pixels(folder/'window.png')==pixels(reference/'window.png')
            checks[f'{width}_{kind}{age}_guest']=hashes(folder/'run.log')==hashes(reference/'run.log')
            checks[f'{width}_{kind}{age}_pcm']=pcm(folder/'audio.wav')==pcm(reference/'audio.wav')
        for kind,saved,target in [('neutral',140,160),('no',150,151),('yes',182,197),('yes',333,350),('yes',333,600)]:
            cold,code=run(width,kind,target,label=f'cold{saved}to{target}',load=frames[kind,saved]/'saved.state')
            checks[f'{width}_{kind}_cold{saved}to{target}_exit']=code==0
            checks[f'{width}_{kind}_cold{saved}to{target}_picture']=pixels(cold/'window.png')==pixels(frames[kind,target]/'window.png')
            checks[f'{width}_{kind}_cold{saved}to{target}_guest']=hashes(cold/'run.log')==hashes(frames[kind,target]/'run.log')
            checks[f'{width}_{kind}_cold{saved}to{target}_pcm']=pcm(cold/'audio.wav')==pcm(frames[kind,target]/'audio.wav')[len(pcm(frames[kind,saved]/'audio.wav')):]
        alternate,code=run(width,'yes',600,label='lle',lle=True)
        checks[f'{width}_lle_exit']=code==0
        for key,compare in [('picture',lambda p:pixels(p/'window.png')),('guest',lambda p:hashes(p/'run.log')),('pcm',lambda p:pcm(p/'audio.wav'))]:
            checks[f'{width}_lle_{key}']=compare(alternate)==compare(frames['yes',600])
        alternate,code=run(width,'yes',197,label='native-art',enabled=False)
        checks[f'{width}_native_art_exit']=code==0
        checks[f'{width}_native_art_guest']=hashes(alternate/'run.log')==hashes(frames['yes',197]/'run.log')
        checks[f'{width}_native_art_pcm']=pcm(alternate/'audio.wav')==pcm(frames['yes',197]/'audio.wav')
        raw=(frames['yes',600]/'saved.state').read_bytes();start=96+struct.unpack_from('<I',raw,20)[0]
        flags,reloads=struct.unpack_from('<II',raw,start+108)
        checks[f'{width}_menu_bank_applied']=bool(flags&2)
        checks[f'{width}_cached_route_eight_reload_payloads_applied']=reloads==509
        fast=[r for r in csv.reader((frames['yes',600]/'exit.csv').open()) if r and r[0]=='fast']
        checks[f'{width}_cached_route_eight_reload_events']=len(fast)==8 and {int(r[5]) for r in fast}==set(range(9))-{1}
        rejected,code=run(width,'yes',350,label='old-unbound-save',load=prior/'layout'/f'{width}-yes-333/saved.state')
        checks[f'{width}_old_package_unbound_save_rejects']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
    for name,path in [('missing',None),('wrong-kind',menu),('damaged',out/'damaged.assets')]:
        if name=='damaged':path.write_bytes(b'BAD DATA')
        folder,code=run(320,'neutral',140,label=name,asset=path)
        checks[name+'_stops_before_guest']=code==6 and b'loaded_state=' not in (folder/'run.log').read_bytes()
    folder,code=run(256,'neutral',140,label='missing-native-art',enabled=False,asset=None)
    checks['native_art_also_requires_package']=code==6
    # The package digest is part of presentation identity, including changes
    # that are structurally valid and have a resealed payload checksum.
    changed=bytearray(native.read_bytes());changed[-1]^=1;changed[56:88]=hashlib.sha256(changed[112:]).digest()
    modified=out/'modified.assets';modified.write_bytes(changed)
    folder,code=run(320,'yes',350,label='changed-package',load=frames['yes',333]/'saved.state',asset=modified)
    checks['changed_package_save_rejects_before_guest']=code==8 and b'loaded_state=' not in (folder/'run.log').read_bytes()
    # Disabling only the bank-apply shortcut exercises the ninth payload. Keep
    # this context separate from the normal warm-cache picture/audio timings.
    profile=out/'cold-bank.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
    cold_env=dict(env,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='0',TLK_CONTINUE_TRANSITION='1')
    comparison={}
    for label,binary in [('installed',base/'player.exe'),('previous',prior/'player.exe')]:
        folder=out/f'cold-bank-{label}';folder.mkdir();comparison[label]=folder
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        cmd=old[0]['commands']['320-yes-197'].copy();cmd[0]=str(binary)
        for flag,value in [('--resource-profile',profile),('--config',folder/'host.ini'),('--frames',4494),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav'),('--final-menu-assets',menu)]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--save-at','4494',str(folder/'saved.state')]
        if label=='installed':cmd+=['--final-native-assets',str(native)]
        actual=dict(cold_env,TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[f'cold-bank-{label}']=cmd;environments[f'cold-bank-{label}']={k:v for k,v in actual.items() if k.startswith('TLK_')}
        checks[f'cold_bank_{label}_exit']=r.returncode==0
    for key,compare in [('picture',lambda p:pixels(p/'window.png')),('guest',lambda p:hashes(p/'run.log')),('pcm',lambda p:pcm(p/'audio.wav'))]:
        checks[f'cold_bank_{key}_unchanged']=compare(comparison['installed'])==compare(comparison['previous'])
    raw=(comparison['installed']/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
    checks['cold_bank_all_nine_payloads_applied']=struct.unpack_from('<I',raw,at+112)[0]==511
    fast=[r for r in csv.reader((comparison['installed']/'exit.csv').open()) if r and r[0]=='fast']
    checks['cold_bank_all_nine_events']=len(fast)==9 and {int(r[5]) for r in fast}==set(range(9))
    paths=[Path(__file__),build,*sources,manifest,native,menu,bank,ROOT/'engine/runner/pride/final/pride_final_assets.inc',ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
    checks['ten_host_decode_paths_removed']=all('TlkMdDecompress(' not in p.read_text() for p in paths[-2:])
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,environments=environments,
        scope='Ten reviewed host payload substitutions use installed data; other guest/startup decoding and sound emulation remain',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
