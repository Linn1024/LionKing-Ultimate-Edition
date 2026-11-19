"""Check selectable captions in actual Windows clients, including lifetime/saves."""
import argparse
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data
from pride_sprite_catalog import bitmap

PREFIX='graphics.titles.pride_lands'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-title-work/player-check')
    parser.add_argument('--build-report',default='final-build3.json')
    args=parser.parse_args();base=ROOT/'build/pride-title-work';out=ROOT/args.out;out.mkdir()
    bp=base/args.build_report;build=json.loads(bp.read_text())
    binary=base/'player/native-engine/tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha
    previous=ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'
    tape=ROOT/'engine/tapes/allbugsF.read.tape';config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    choices={'native':'','art':PREFIX+'.frames = md\n','palette':PREFIX+'.palette = md\n',
             'position':PREFIX+'.position = md\n','duration':PREFIX+'.duration = md\n',
             'visual':PREFIX+' = md\n'+PREFIX+'.duration = snes\n','all':PREFIX+' = md\n',
             'hud':'graphics.hud.palette = md\n'}
    checks={};commands=[];observations=[]
    def run(name,field,width=256,choice='native',seed=None,save=None,old=False,lle=False):
        folder=out/name;folder.mkdir();profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\n'+('display.viewport = md\n' if width==320 else '')+choices[choice])
        cmd=[previous if old else binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--input-polled',seed[1] if seed else tape,
             '--frames',field,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
             '--dump-scene',folder/'scene.json','--wav',folder/'audio.wav','--wav-seconds',60]
        if seed:cmd+=['--load',seed[0]]
        if save:cmd+=['--save-at',field,save]
        if lle:cmd+=['--lle']
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
        return dict(folder=folder,pixels=pixels(folder/'window.png'),hashes=hashes(folder/'run.log'),
                    pcm=wav_data(folder/'audio.wav'),scene=json.loads((folder/'scene.json').read_text()))
    ready=out/'before-caption.state';saved=run('seed',930,save=ready,old=True)
    used=int(re.search(r'tape_words_used=(\d+)',(saved['folder']/'run.log').read_text()).group(1))
    suffix=out/'after930.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:]);seed=(ready,suffix)
    md=(ROOT/'Lion King, The (World).md').read_bytes();snes=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    pieces=[]
    for i in range(11):
        w,h,x,y,flags,transfer,source=struct.unpack_from('>6HI',md,0x1d5dac+24+i*16)
        pieces.append((x-160,y-72,w,h,source))
    md_image=bitmap(md,pieces,True,with_origin=True)
    md_palette=[sum(((c>>s&7)*4+((c>>s&7)>>2))<<(n*5) for n,s in enumerate((1,5,9))) for c in struct.unpack_from('>16H',md,0x1d78aa)]
    for width in (256,320):
        for field in (950,964,980,1000,1032,1056,1080,1100):
            native=run(f'{width}-{field}-native',field,width,seed=seed)
            mixed=run(f'{width}-{field}-all',field,width,'all',seed)
            checks[f'{width}/{field}/guest_audio_preserved']=native['hashes']==mixed['hashes'] and native['pcm']==mixed['pcm']
            parts=[p for p in native['scene']['pieces'] if p.get('title_owner')]
            detail=dict(width=width,field=field,title_pieces=len(parts))
            if parts:
                timer=parts[0]['actor_timer'];detail['timer']=timer
                if timer>50:
                    checks[f'{width}/{field}/visible_change']=native['pixels']!=mixed['pixels']
                    bx,by,bw,bh,data=md_image;pw,ph,image=mixed['pixels'];wrong=[]
                    for i,c in enumerate(data):
                        if not c:continue
                        x=width//2+bx+i%bw;y=72+by+i//bw
                        bright=mixed['scene']['lines'][y]['brightness'];color=md_palette[c]
                        expected=tuple((((color>>s&31)<<3)|((color>>s&31)>>2))*bright//15 for s in (0,5,10))
                        if image[(y*3+1)*pw+x*3+1]!=expected:wrong.append([x,y])
                    detail['md_pixel_mismatches']=wrong[:12]
                    checks[f'{width}/{field}/original_md_art_pixels']=not wrong
                else:
                    longer=run(f'{width}-{field}-visual',field,width,'visual',seed)
                    checks[f'{width}/{field}/shorter_md_duration']=mixed['pixels']!=longer['pixels']
            else:
                checks[f'{width}/{field}/no_stray_caption']=native['pixels']==mixed['pixels']
            observations.append(detail)
            print(width,field,detail,flush=True)
    for width in (256,320):
        rows={choice:run(f'independent-{width}-{choice}',1000,width,choice,seed) for choice in choices}
        native=rows['native'];old=run(f'previous-{width}',1000,width,seed=seed,old=True)
        checks[f'{width}/native_client_unchanged']=native['pixels']==old['pixels']
        checks[f'{width}/all_choices_keep_guest_pcm']=all(r['hashes']==native['hashes'] and r['pcm']==native['pcm'] for r in rows.values())
        checks[f'{width}/independent_art_palette_position']=len({tuple(rows[c]['pixels'][2]) for c in ('native','art','palette','position','visual')})==5
        checks[f'{width}/early_duration_preserves_native_pixels']=rows['duration']['pixels']==native['pixels']
        checks[f'{width}/early_duration_independent']=rows['visual']['pixels']==rows['all']['pixels']
        state=out/f'active-{width}.state';saved=run(f'active-save-{width}',999,width,seed=seed,save=state,old=True)
        used=int(re.search(r'tape_words_used=(\d+)',(saved['folder']/'run.log').read_text()).group(1))
        tail=out/f'after999-{width}.polled.tape';tail.write_bytes(suffix.read_bytes()[used*2:])
        for lle in (False,True):
            resumed=run(f'active-resume-{width}-{lle}',1000,width,'all',(state,tail),lle=lle)
            checks[f'{width}/active_save_{lle}']=all(resumed[k]==rows['all'][k] for k in ('pixels','hashes'))
    paths=[Path(__file__),bp,ROOT/'build/pride-title-work/assets2/report.json',ROOT/'build/pride-title-original2/report.json']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
                full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'actual caption checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
