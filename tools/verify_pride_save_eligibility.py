"""Compare actual predecessor/new save predicates across busy and native states."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def function(text, name):
    start = text.index('static int ' + name + '(void) {')
    end = text.index('\n}\n', start) + 3
    return text[start:end]


def main():
    old = ROOT / 'build/pride-rng-player5'
    new = ROOT / 'build/pride-rng-player7'
    for folder in (old, new):
        r = bound(folder / 'build-report.json')
        assert digest(folder / 'player.exe') == r['binary_sha256']
    out = new / 'eligibility-equivalence'
    out.mkdir()
    predicate = ROOT / 'engine/runner/tlk_pride_save_scene.inc'
    header = ROOT / 'engine/runner/tlk_pride_save_context.h'
    source = out / 'compare.c'
    source.write_text('''#include <stdio.h>
#include "tlk_pride_save_context.h"
static unsigned owner_installed,restore_installed,have_return,owner_waiting;
static unsigned grounded_waiting,scene_active,active;
static struct { unsigned started; } owner_scene;
static void *preparation_pending;
static unsigned level,descriptor,cub_age,health,word_1ff90,phase;
static unsigned ow(unsigned address) {
    switch(address) {
    case 0x1ff9e:return level;
    case 0x2000:return cub_age;
    case 0x2004:return health;
    case 0x1ff90:return word_1ff90;
    case 8:return phase;
    default:return 0;
    }
}
static unsigned ol(unsigned address) { return address==0xdf?descriptor:0; }
''' + predicate.read_text() +
        function((old / 'host.i').read_text(), 'practice_context_ready').replace('practice_context_ready', 'previous_ready') +
        function((new / 'host.i').read_text(), 'practice_context_ready').replace('practice_context_ready', 'owned_ready') + '''
int main(void) {
    const unsigned descriptors[]={0xc00387,0xc0080d,0xc005ab,0,0xc00388,0xc105ab};
    unsigned checks=0; int token=1;
    for(unsigned flags=0;flags<512;flags++) {
        owner_installed=flags&1;restore_installed=flags&2;have_return=flags&4;
        owner_scene.started=flags&8;preparation_pending=flags&16?&token:NULL;
        owner_waiting=flags&32;grounded_waiting=flags&64;
        scene_active=flags&128;active=flags&256;
        for(unsigned d=0;d<6;d++)for(phase=0;phase<8;phase++)for(unsigned variant=0;variant<10;variant++) {
            descriptor=descriptors[d];level=0;cub_age=0;health=4;word_1ff90=0;
            switch(variant) {
            case 1:level=1;break;case 2:level=65535;break;
            case 3:cub_age=1;break;case 4:cub_age=65535;break;
            case 5:health=0;break;case 6:health=65535;break;
            case 7:word_1ff90=1;break;case 8:word_1ff90=65535;break;
            case 9:phase+=65536;break;
            }
            if(previous_ready()!=owned_ready())return 1;
            checks++;
            if(variant==9)phase-=65536;
        }
    }
    if(TlkPrideIdleSaveEligible(NULL))return 2;
    printf("PASS %u predecessor/owned predicate comparisons\\n",checks);
    return 0;
}
''')
    exe = out / 'compare.exe'
    cmd = ['C:/mingw32/bin/gcc.exe', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
           '-I' + str(header.parent), str(source), '-o', str(exe)]
    subprocess.run(cmd, check=True, timeout=60)
    result = subprocess.check_output([str(exe)], text=True, timeout=30)
    assert result.strip() == 'PASS 245760 predecessor/owned predicate comparisons'
    log = out / 'test.log'
    log.write_text(result)
    paths = [Path(__file__), header, predicate, old / 'build-report.json', new / 'build-report.json',
             old / 'host.i', new / 'host.i']
    report = dict(result='PASS', compared_contexts=245760, null_context_rejected=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in (source, exe, log)},
                  full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(result.strip(), flush=True)


if __name__ == '__main__':
    main()
