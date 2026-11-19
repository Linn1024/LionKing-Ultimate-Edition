"""Verify independent Continue-token artwork/palette using a genuine old save."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-continue-token46';build_path=base/'build-report.json';build=bound(build_path)
    out=base/'artwork-verification';out.mkdir()
    source=ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json';prior=bound(source)
    component_path=base/'component/report.json';assert bound(component_path)['result']=='PASS'
    asset_path=ROOT/'build/pride-continue-token-assets/build-report.json';assets=bound(asset_path)
    template=prior['commands']['full-aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    commands={};checks={};clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(label,frames=2520,old=False,save=False,load=None,tape=None,choices=None,lle=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        if not old:
            cmd[0]=str(base/'player.exe');cmd[cmd.index('--sprite-assets')+1]=str(asset_path.parent/'sprites.assets')
        for flag,value in [('--frames',frames),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if choices:
            with (folder/'resources.ini').open('a') as f:
                f.write('\ngraphics.sprites.pickups.continue_token.frames = '+choices[0]+'\ngraphics.sprites.pickups.continue_token.palette = '+choices[1]+'\n')
        if save:cmd+=['--save-at',str(frames),str(folder/'saved.state')]
        if load:cmd+=['--load',str(load)]
        if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
        if lle:cmd.append('--lle')
        cmd+=['--hash-at',','.join(map(str,range(2506,frames+1)))]
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_SPRITE_REPORT=str(folder/'sprites.json'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0;print(label,rc,flush=True);return folder
    seed=run('old44-seed',frames=2505,old=True,save=True)
    row=json.loads((seed/'tree.jsonl').read_text().splitlines()[-1]);assert row['field']==2505
    original_tape=Path(template[template.index('--input-polled')+1]);suffix=out/'suffix.tape';suffix.write_bytes(original_tape.read_bytes()[row['poll_index']*2:])
    state=seed/'saved.state';state_sha=digest(state)
    outputs={'old':run('old44-cold',old=True,load=state,tape=suffix)}
    for label,choices,lle in [('native',('snes','snes'),False),('frames',('md','snes'),False),('palette',('snes','md'),False),('both',('md','md'),False),('both-lle',('md','md'),True)]:
        outputs[label]=run(label,load=state,tape=suffix,choices=choices,lle=lle)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda p:re.findall(pattern,(p/'run.log').read_text())
    baseline=outputs['old'];expected=hashes(baseline)
    checks['all15_guest_fields_preserved']=len(expected)==15 and all(hashes(p)==expected for p in outputs.values())
    for label,p in outputs.items():
        for name in ('audio.wav','scene.json','events.csv'):
            checks[label+'_'+name+'_preserved']=digest(p/name)==digest(baseline/name)
    checks['native_artwork_unchanged']=digest(outputs['native']/'window.png')==digest(baseline/'window.png')
    for name in ('window.png','sprites.json'):
        checks['modes_'+name]=digest(outputs['both']/name)==digest(outputs['both-lle']/name)
    width,height,native=pixels(baseline/'window.png');scene=json.loads((baseline/'scene.json').read_text())
    sun=[p for p in scene['pieces'] if p['actor_descriptor']==0xc586cc and p['pose'] in (0xc6f764,0xc6f79b,0xc6f7ce,0xc6f801)]
    assert sun and width==640 and height==448 and 'gameplay.camera = md' in (baseline/'resources.ini').read_text()
    left=max(0,min(p['screen'][0] for p in sun)-2)*2;right=min(320,max(p['screen'][0]+p['size'] for p in sun)+2)*2
    top=max(0,min(p['screen'][1] for p in sun)-2)*2;bottom=min(224,max(p['screen'][1]+p['size'] for p in sun)+2)*2
    differences={}
    for label in ('frames','palette','both'):
        w,h,image=pixels(outputs[label]/'window.png');changed=[i for i,(a,b) in enumerate(zip(native,image)) if a!=b]
        checks[label+'_visible']=bool(changed) and (w,h)==(width,height)
        checks[label+'_only_sun_region_changes']=bool(changed) and all(left<=i%width<right and top<=i//width<bottom for i in changed)
        differences[label]=dict(changed_pixels=len(changed),bounds=[min(i%width for i in changed),min(i//width for i in changed),max(i%width for i in changed)+1,max(i//width for i in changed)+1] if changed else None)
    checks['artwork_palette_independent']=digest(outputs['both']/'window.png')!=digest(outputs['frames']/'window.png') and digest(outputs['both']/'window.png')!=digest(outputs['palette']/'window.png')
    for label in ('frames','both','both-lle'):
        checks[label+'_four_md_frames_used']=json.loads((outputs[label]/'sprites.json').read_text())['seen_by_role']['continue_token']==4
    old_record=(ROOT/'build/pride-sprite-assets/sprites.assets').read_bytes();new_record=(asset_path.parent/'sprites.assets').read_bytes()
    checks['installed_pixel_payload_unchanged']=old_record[192:]==new_record[192:]
    checks['installed_policy_digest_changed']=old_record[88:120]!=new_record[88:120]
    checks['old_save_unchanged']=digest(state)==state_sha
    paths=[Path(__file__),build_path,source,component_path,asset_path,state]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,differences=differences,
                allowed_sun_region=[left,top,right,bottom],native_timing_and_audio_retained=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],differences,flush=True)


if __name__=='__main__':main()
