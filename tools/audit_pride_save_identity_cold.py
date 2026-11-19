"""Compare stable-identity cold output with the preceding executable-bound player."""
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-save-identity2';out=base/'preceding-cold';out.mkdir();checks={};paths=[Path(__file__)];commands={}
    old_path=ROOT/'build/pride-legacy-save/player/build-report.json';old=bound(old_path);paths.append(old_path)
    binary=old_path.parent/'mixed.exe';assert digest(binary)==old['runs']['mixed']['binary_sha256']
    for profile in ('native','md'):
        path=base/'verified'/profile/'report.json';r=bound(path);assert r['result']=='PASS';paths.append(path)
        folder=out/profile;folder.mkdir();current=path.parent/'author-a';cmd=list(r['commands']['author-a']);cmd[0]=str(binary)
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n');cmd[cmd.index('--config')+1]=str(config)
        for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
        cmd[cmd.index('--save-at')+2]=str(folder/'owned.state');commands[profile]=cmd
        env=environment(folder);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv');env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv')
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        checks[profile+'/exit']=p.returncode==0
        rows=lambda f:re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(f/'run.log').read_text())
        checks[profile+'/every_native_field']=rows(folder)==rows(current) and len(rows(current))==3000
        checks[profile+'/complete_pcm']=wav_data(folder/'audio.wav')==wav_data(current/'audio.wav')
        checks[profile+'/whole_client']=pixels(folder/'window.png')==pixels(current/'window.png')
        checks[profile+'/every_md_stem']=read_rows(folder/'stems.csv')==read_rows(current/'stems.csv')
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json'):
            checks[profile+'/'+name]=(folder/name).exists()==(current/name).exists() and (not (folder/name).exists() or digest(folder/name)==digest(current/name))
        for file in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        print(profile,'preceding cold compared',flush=True)
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
