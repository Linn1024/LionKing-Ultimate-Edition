"""Full All Bugs tracked fields and neutral production pilot for maintained226."""
from pathlib import Path
import json
import shutil
import subprocess
import uuid
from audit_scenes import ROOT

pilot_root239=None
def pilot_folder239(folder):
    global pilot_root239
    if pilot_root239 is None:
        assert shutil.disk_usage('G:/').free>24*1024*1024,'Need24MiB on G for two pilot WAVs'
        assert shutil.disk_usage(ROOT).free>12*1024*1024,'Need12MiB on C for tracked logs'
        pilot_root239=Path('G:/lionKing-menu239-pilot-'+uuid.uuid4().hex)
        assert not pilot_root239.exists();pilot_root239.mkdir()
        (folder.parent/'pilot-storage.json').write_text(json.dumps(dict(
            target=str(pilot_root239),purpose='Owned pilot audio and logs; accessed by junctions under ignored build. No existing evidence moved/deleted.'),indent=2)+'\n')
    target=pilot_root239/folder.name;assert target.parent==pilot_root239;target.mkdir()
    quote=lambda p:"'"+str(p).replace("'","''")+"'"
    command='New-Item -ItemType Junction -Path '+quote(folder)+' -Target '+quote(target)+' | Out-Null'
    subprocess.run(['powershell.exe','-NoProfile','-Command',command],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert folder.resolve()==target.resolve()

def capture_files239(out):
    files={p for p in out.rglob('*') if p.is_file()}
    for name in ('pilot-control','pilot-observer'):
        files.update(p for p in (out/name).iterdir() if p.is_file())
    return sorted(files)

script=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=script.read_text().replace('pride-checkpoint-animation52','pride-menu226-integrated')
source=source.replace('paths = [Path(__file__), build_path,','paths = [Path(__file__),script,build_path,')
anchor='        folder.mkdir()';assert source.count(anchor)==1
source=source.replace(anchor,'        if frames==3000:pilot_folder239(folder)\n        else:folder.mkdir()')
source=source.replace("for p in out.rglob('*') if p.is_file()","for p in capture_files239(out)")
exec(compile(source,str(script),'exec'))
