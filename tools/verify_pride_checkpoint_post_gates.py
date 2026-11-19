"""Promote the verified local checkpoint build, then check packaging and media."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interaction',action='store_true',help='Require both interaction matrices and generation3 headless gates')
    args=parser.parse_args()
    generation=3 if args.interaction else 2
    out = ROOT/'build/pride-checkpoint-player'
    player = ROOT/'engine/build-win/tlk_sdl.exe'
    identity = digest(player)
    headless = digest(ROOT/'engine/build-win/tlk_headless.exe')
    required = ['windows-5400','windows-3685','state','switch']
    if args.interaction:
        required += ['windows-3657','windows-3662']
    for folder in required:
        report = json.loads((out/folder/'report.json').read_text())
        assert report['result'] == 'PASS' and report['candidate_sha256'] == identity,folder
        for path,sha in report.get('source_sha256',{}).items():
            assert digest(ROOT/path) == sha,path
    for name in ('play','allbugs'):
        report = json.loads((out/f'native{generation}/{name}-report.json').read_text())
        assert report['result'] == 'PASS' and report['binary_sha256'] == headless
    for name in ('gameplay','gameplay256'):
        report = json.loads((out/f'completion{generation}/{name}/report.json').read_text())
        assert report['result'] == 'PASS' and report['executed_host_sha256'] == headless and report['checkpoint_sources']
    # Local build artifact replacement; source ROMs, settings and saves stay intact.
    shutil.copyfile(player,ROOT/'dist/LionKing.exe')
    reports = {}

    def run(name,script,args=()):
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run([sys.executable,str(ROOT/'tools'/script),*map(str,args)],cwd=ROOT,
                           stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        assert digest(player) == identity and digest(ROOT/'dist/LionKing.exe') == identity

    common = ['--checkpoint','--media','--output-root',f'build/pride-checkpoint-player/completion{generation}',
              '--player','engine/build-win/tlk_sdl.exe']
    run(f'media{generation}-320','verify_pride_authored_route.py',[
        '--tape','build/pride-normal-completion/route.polled.tape','--frames','5000',*common])
    run(f'media{generation}-256','verify_pride_authored_route.py',[
        '--tape','build/pride-normal-completion/route256.polled.tape','--frames','5500','--width','256',*common])
    run('windows-ui','verify_windows.py')
    run('installer','verify_installer.py')
    run('launchers','verify_next_launchers.py')
    env = os.environ.copy()
    env.update(SDL_VIDEO_DRIVER='dummy',SDL_VIDEODRIVER='dummy')
    with (out/'remap.log').open('wb') as log:
        subprocess.run([str(player),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--no-audio','--selftest-remap'],
                       cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    assert 'remap_selftest: PASS (0 failed)' in (out/'remap.log').read_text(errors='replace')
    for relative in ('build/windows-smoke/report.json','build/setup-verification/report.json',
                     'build/next-level-launchers/report.json',
                     f'build/pride-checkpoint-player/completion{generation}/media/report.json',
                     f'build/pride-checkpoint-player/completion{generation}/media256/report.json'):
        report = json.loads((ROOT/relative).read_text())
        assert report['result'] == 'PASS',relative
        reports[relative] = digest(ROOT/relative)
    assert digest(player) == identity and digest(ROOT/'dist/LionKing.exe') == identity
    assert digest(ROOT/'engine/build-win/tlk_headless.exe') == headless
    result = dict(result='PASS',scope=__doc__,player_sha256=identity,headless_sha256=headless,
        interaction_image_matrices_required=args.interaction,evidence_generation=generation,
        reports_sha256=reports,source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        full_first_level_fidelity_complete=False)
    (out/'post-gates.json').write_text(json.dumps(result,indent=2)+'\n')
    info = ROOT/'dist/build-info.txt'
    raw = info.read_bytes()
    try:
        text = raw.decode('utf-16' if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    text = '\n'.join(line for line in text.splitlines() if not line.startswith('Checkpoint source adapter:'))
    info.write_text(text+'\nCheckpoint source adapter: independently selectable Pride head frames/palette; '+identity+'\n',encoding='utf-8')
    print('Local checkpoint build promoted; media, F10/UI, installer, nine launchers and remapping PASS',flush=True)


if __name__ == '__main__':
    main()
