"""Verify installed real-driver title upload in normal/LLE execution and cold saves."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-title-upload16');parser.add_argument('--output',default='verification');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-title-native15/verification/report.json';previous=bound(source)
    prototype=ROOT/'build/pride-title-upload-fast5/report.json';probe=bound(prototype)
    life=ROOT/'build/pride-title-upload-lifecycle5/report.json';life_data=bound(life)
    manifest=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank/install.json';info=json.loads(manifest.read_text());bank=manifest.parent/info['title_bank_assets']['file']
    out=base/args.output;out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(width,label,age,lle=False,load=None,save=False,tape=None,asset=bank,native_art=False,native_control=False,audio=False):
        folder=out/f'{width}-{label}';folder.mkdir()
        key=f'{width}-native-control2600' if native_control else f'{width}-700'
        cmd=previous['commands'][key].copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--config',out/'host.ini'),('--frames',4444+age),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if asset is not None:cmd+=['--title-bank-assets',str(asset)]
        if lle:cmd+=['--lle']
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(4444+age),str(folder/'saved.state')]
        if tape:cmd[cmd.index('--input')+1]=str(tape)
        if audio:
            for flag in ('--no-audio','--no-pace'):
                if flag in cmd:cmd.remove(flag)
        env=dict(clean,TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        if not (native_art or native_control):env['TLK_FINAL_MD_ART']='1'
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;print(folder.name,r.returncode,flush=True);return folder,r.returncode
    def same(prefix,a,b,skip=0):
        if not (a/'window.png').exists():checks[prefix+'_client']=checks[prefix+'_guest']=checks[prefix+'_pcm']=False;return
        checks[prefix+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[prefix+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[prefix+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for width in (256,320):
        live,code=run(width,'normal700',700);checks[f'{width}_normal_exit']=code==0
        lle,code=run(width,'lle700',700,lle=True);checks[f'{width}_lle_exit']=code==0
        same(f'{width}_normal_lle',live,lle)
        same(f'{width}_prototype_preserved',live,prototype.parent/str(width))
        if (live/'window.png').exists():
            rows=list(csv.reader((live/'exit.csv').open()));copies=[r for r in rows if r and r[0]=='title_upload']
            checks[f'{width}_sixteen_packets']=len(copies)==16 and {int(r[5]) for r in copies}==set(range(16))
            first=next(int(r[1]) for r in rows if r[0]=='frame' and r[2]=='c005ab' and int(r[5]))
            checks[f'{width}_first_title372']=first==372;observations[str(width)]=dict(first_title=first,remaining_fields=first-370)
        frames={700:live}
        for age in (366,367,368,372):
            folder,code=run(width,str(age),age,save=age!=372);checks[f'{width}_{age}_exit']=code==0;frames[age]=folder
        same(f'{width}_pre_upload_unchanged',frames[366],source.parent/f'{width}-366')
        for saved,target in ((366,372),(367,372),(368,372),(367,700)):
            folder,code=run(width,f'cold{saved}to{target}',target,load=frames[saved]/'saved.state');checks[f'{width}_cold{saved}to{target}_exit']=code==0
            same(f'{width}_cold{saved}to{target}',folder,frames[target],len(pcm(frames[saved]/'audio.wav')))
        alternate,code=run(width,'native-art700',700,native_art=True);checks[f'{width}_native_art_exit']=code==0;same(f'{width}_art_independence',alternate,live)
        control,code=run(width,'native-control2600',2600,native_control=True);checks[f'{width}_native_control_exit']=code==0;same(f'{width}_native_final_unchanged',control,source.parent/f'{width}-native-control2600')
        template=life_data['commands'][f'{width}-new-game2000'];tape=Path(template[template.index('--input')+1])
        new,code=run(width,'new-game2000',2000,tape=tape,save=True);checks[f'{width}_new_game_exit']=code==0
        same(f'{width}_new_game_prototype',new,life.parent/f'{width}-new-game2000')
        if (new/'saved.state').exists():
            raw=(new/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
            checks[f'{width}_owner_retired']=struct.unpack_from('<I',raw,at+100)[0]==struct.unpack_from('<I',raw,at+112)[0]==0
        cold,code=run(width,'cold-new-game2000',2000,tape=tape,load=frames[367]/'saved.state');checks[f'{width}_cold_new_game_exit']=code==0;same(f'{width}_cold_new_game',cold,new,len(pcm(frames[367]/'audio.wav')))
        rejected,code=run(width,'old-unbound-save',700,load=source.parent/f'{width}-400/saved.state')
        checks[f'{width}_old_save_rejects_before_guest']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
    for label,asset in [('missing',None),('wrong-kind',ROOT/'build/pride-title-bank-installed/verification/native.assets'),('damaged',out/'damaged.assets')]:
        if label=='damaged':asset.write_bytes(b'BAD DATA')
        folder,code=run(320,label,700,asset=asset)
        checks[label+'_stops_before_guest']=code==6 and b'loaded_state=' not in (folder/'run.log').read_bytes()
    changed=bytearray(bank.read_bytes());changed[-1]^=1;changed[56:88]=hashlib.sha256(changed[112:]).digest();modified=out/'modified.assets';modified.write_bytes(changed)
    folder,code=run(320,'changed-bank-save',700,asset=modified,load=out/'320-367/saved.state')
    checks['changed_program_rejects_before_guest']=code==8 and b'loaded_state=' not in (folder/'run.log').read_bytes()
    audio,code=run(320,'real-audio372',372,audio=True);checks['real_audio_exit']=code==0;same('real_audio_endpoint',audio,out/'320-372')
    paths=[Path(__file__),build,source,prototype,life,manifest,bank,ROOT/'engine/runner/pride/final/pride_final_title_bank.inc',ROOT/'engine/runner/pride/final/pride_final_save.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())

if __name__=='__main__':main()
