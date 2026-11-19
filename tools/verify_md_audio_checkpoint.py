"""Run exact same-process/new-process MD checkpoints and verify source packaging."""
import hashlib
import json
import subprocess
import zipfile
from audit_scenes import ROOT


def main():
    out=ROOT/'build/md-audio-checkpoint';out.mkdir(exist_ok=True)
    base=[str(ROOT/'engine/build-win/tlk_md_sound_state_test.exe'),str(ROOT/'Lion King, The (World).md')]
    for mode in ('write','read'):
        log=out/(mode+'.log')
        with log.open('wb') as stream:
            subprocess.run(base+['--'+mode,str(out/'checkpoint')],cwd=ROOT,stdout=stream,
                           stderr=subprocess.STDOUT,check=True,timeout=120)
        assert 'PASS' in log.read_text()
    subprocess.run(['python3.12.exe',str(ROOT/'tools/prepare_md_backend.py'),'check'],cwd=ROOT,check=True)
    stamp=json.loads((ROOT/'.tools/genesis-plus-gx/tlk-build.json').read_text())
    dll=ROOT/'dist/genesis_plus_gx_libretro.dll'
    assert stamp['dll_sha256']==hashlib.sha256(dll.read_bytes()).hexdigest()
    with zipfile.ZipFile(ROOT/'dist/source/Genesis-Plus-GX-source.zip') as archive:
        for name in ('core/state.c','core/system.c','core/sound/sound.c','core/sound/blip_buf.c'):
            assert archive.read('Genesis-Plus-GX/'+name)==(ROOT/'.tools/genesis-plus-gx'/name).read_bytes()
        assert archive.read('tlk-patches/0001-audio-continuation.patch')==(ROOT/'engine/patches/genesis-plus-gx/0001-audio-continuation.patch').read_bytes()
    pcm=(out/'checkpoint.pcm').read_bytes();assert len(pcm)==32000
    report={'result':'PASS','scope':__doc__,'stereo_frames_exact':8000,
            'new_process_exact':True,'checksum_valid_backend_rejection_atomic':True,
            'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'backend':stamp,
            'matching_modified_source_packaged':True}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exact MD audio checkpoints and matching source package PASS',flush=True)


if __name__=='__main__':main()
