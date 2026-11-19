"""Build the packaged backend source and replay an actual packaged checkpoint."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile
from audit_scenes import ROOT


def main():
    out=ROOT/'build/md-backend-source';out.mkdir(exist_ok=True)
    folder=Path(tempfile.mkdtemp(prefix='source-',dir=out))
    with zipfile.ZipFile(ROOT/'dist/source/Genesis-Plus-GX-source.zip') as archive:archive.extractall(folder)
    env=os.environ.copy()
    git=Path(shutil.which('git')).resolve()
    env['PATH']=str(git.parent.parent/'usr/bin')+os.pathsep+str(git.parent)+os.pathsep+env['PATH']
    command=['mingw32-make','-f','Makefile.libretro','platform=win','HAVE_CHD=0',
             'HAVE_SYS_PARAM=0','HOOK_CPU=1','CPPFLAGS=-fcommon',
             'SHARED=-shared -static-libgcc -Wl,--export-all-symbols','-j8']
    with (out/'build.log').open('wb') as log:
        subprocess.run(command,cwd=folder/'Genesis-Plus-GX',env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    shutil.copy2(ROOT/'engine/build-win/tlk_md_sound_state_test.exe',folder/'tlk_md_sound_state_test.exe')
    shutil.copy2(folder/'Genesis-Plus-GX/genesis_plus_gx_libretro.dll',folder/'genesis_plus_gx_libretro.dll')
    with (out/'checkpoint.log').open('wb') as log:
        subprocess.run([str(folder/'tlk_md_sound_state_test.exe'),str(ROOT/'Lion King, The (World).md'),
                        '--read',str(ROOT/'build/md-audio-checkpoint/checkpoint')],cwd=folder,
                       stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,
        'source_archive_built_without_original_checkout':True,'packaged_checkpoint_continuation_exact':True,
        'rebuild_directory':str(folder)},indent=2)+'\n')
    print('Packaged MD source builds and reproduces the original checkpoint PCM PASS',flush=True)


if __name__=='__main__':main()
