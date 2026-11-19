"""Retain current-format replay exactly against the preceding player."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-legacy-save';build_path=base/'player/build-report.json';build=bound(build_path);checks={};reports={};paths=[Path(__file__),build_path];commands={}
    out=base/'current-format';out.mkdir()
    for case,host,prior_folder,prior_exe in (('native','native',ROOT/'build/pride-tree-help2/plain-native','native.exe'),
                                           ('mixed-native','mixed',ROOT/'build/pride-tree-help2','singlepass.exe'),
                                           ('mixed-md','mixed',ROOT/'build/pride-tree-help2','singlepass.exe')):
        path=base/'verified'/case/'report.json';r=bound(path);assert r['result']=='PASS' and all(r['checks'].values());paths.append(path);reports[case]=digest(path)
        prior_path=prior_folder/'build-report.json';prior=bound(prior_path);paths.append(prior_path)
        binary=prior_folder/prior_exe;assert digest(binary)==prior['binary_sha256']
        folder=out/case;folder.mkdir();current=path.parent/'control';cmd=list(r['commands']['control']);cmd[0]=str(binary)
        for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
        commands[case]=cmd;env=environment(folder);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        checks[case+'/exit']=p.returncode==0
        import re
        hashes=lambda f:re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(f/'run.log').read_text())
        checks[case+'/all_guest_fields']=hashes(folder)==hashes(current) and len(hashes(current))==60
        checks[case+'/whole_client']=pixels(folder/'window.png')==pixels(current/'window.png')
        checks[case+'/whole_guest']=pixels(folder/'guest.png')==pixels(current/'guest.png')
        checks[case+'/whole_pcm']=wav_data(folder/'audio.wav')==wav_data(current/'audio.wav')
        checks[case+'/all_md_stems']=read_rows(folder/'stems.csv')==read_rows(current/'stems.csv')
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json'):
            checks[case+'/'+name]=(folder/name).exists()==(current/name).exists() and (not (folder/name).exists() or digest(folder/name)==digest(current/name))
        for file in folder.glob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
