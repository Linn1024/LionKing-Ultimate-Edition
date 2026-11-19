"""Build fresh bank tests without replacing frozen runtime/test binaries."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-continue-bank-checks2';out.mkdir();build=ROOT/'engine/build-win'
    reference=ROOT/'build/pride-continue-bank-ready-probe/capture/report.json'
    assert bound(reference)['result']=='PROTOTYPE_PASS'
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    bank=next(r for r in db if r.get('file','').endswith('/tlk_native_bank.c') and '/tlk_native_bank_test.dir/' in r['output'])
    test=next(r for r in db if r.get('file','').endswith('/native_bank_test.c'))
    objects={}
    for name,entry,source in [('bank',bank,ROOT/'engine/runner/tlk_native_bank.c'),
        ('health',test,ROOT/'engine/tests/native_bank_test.c'),
        ('continue',test,ROOT/'engine/tests/native_bank_continue_test.c')]:
        cmd=argv(entry['command']);obj=out/(name+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(name+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(name+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        objects[name]=obj
    lines=(build/'build.ninja').read_text().splitlines();start=next(n for n,s in enumerate(lines) if s.startswith('build tlk_native_bank_test.exe:'))
    original=lines[start].split(': ',1)[1].split(' ',1)[1].split(' |')[0].split()
    libraries=next(s.split(' = ',1)[1] for s in lines[start+1:] if s.startswith('  LINK_LIBRARIES ='))
    original+=argv('link '+libraries)[1:]
    for name in ('health','continue'):
        inputs=original.copy()
        for old,new in [(bank['output'],objects['bank']),(test['output'],objects[name])]:
            assert inputs.count(old)==1;inputs[inputs.index(old)]=new.as_posix()
        rsp=out/(name+'.rsp');rsp.write_text(subprocess.list2cmdline(inputs))
        cmd=['C:/mingw32/bin/g++.exe','-O3','-static','@'+str(rsp),'-o',str(out/(name+'.exe'))]
        with (out/(name+'-link.log')).open('wb') as log:
            subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    fixture=ROOT/'build/pride-native-bank/native-control';commands=[]
    for mode in ('--write','--read'):
        cmd=[out/'health.exe',ROOT/'Lion King, The (USA).sfc',fixture/'capture-apu.bin',fixture/'capture-wram.bin',
            fixture/'before-apu.bin',fixture/'before-wram.bin',mode,out/'bank.record',out/'continued-apu.bin']
        commands.append(list(map(str,cmd)))
        with (out/('health-'+mode[2:]+'.log')).open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    current=reference.parent
    cmd=[out/'continue.exe',ROOT/'Lion King, The (USA).sfc',current/'boot/captured-apu.bin',current/'boot/captured-wram.bin',
        current/'warm/before-apu.bin',current/'warm/before-wram.bin']
    commands.append(list(map(str,cmd)))
    with (out/'continue.log').open('wb') as log:
        subprocess.run(commands[-1],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    logs={name:(out/(name+'.log')).read_text() for name in ('health-write','health-read','continue')}
    assert all('0 failures' in text for text in logs.values()),logs
    paths=[Path(__file__),reference,ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/runner/tlk_native_bank.h',
        ROOT/'engine/tests/native_bank_test.c',ROOT/'engine/tests/native_bank_continue_test.c']
    report=dict(result='PASS',logs=logs,commands=commands,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',logs,flush=True)


if __name__=='__main__':main()
