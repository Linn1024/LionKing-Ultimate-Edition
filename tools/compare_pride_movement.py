"""Compare controlled original-game movement, including fixed-point fractions.

Sixteen short flat-ground cases do not prove complete movement/combat equivalence.
Initial X offsets are normalized; roar charge is reported separately because the
ready-states have different idle phases.
"""
import json
from md_lab import ROOT


def value(row,source,field):
    word=lambda offset:row['words'][offset//2]
    if field in ('health','roar'):return row[field]
    if field in ('x','y'):
        return row[field]*65536+word(0x34 if field=='x' else 0x36)
    offset=0x38 if field=='vx' else 0x3c
    integer,fraction=(word(offset+2),word(offset)) if source=='snes' else (word(offset),word(offset+2))
    integer=integer if integer<32768 else integer-65536
    return integer*65536+fraction


def main():
    out=ROOT/'build/pride-movement'
    snes=json.loads((out/'snes.json').read_text())['cases']
    md=json.loads((out/'md.json').read_text())['cases']
    assert snes.keys()==md.keys(),'Regenerate both sources after changing cases'
    report={'scope':__doc__,'cases':{}}
    for name,rows in snes.items():
        assert len(rows)==len(md[name])==64
        differences={};roar=[]
        for index,(native,other) in enumerate(zip(rows,md[name])):
            assert native['pad']==other['pad'],'Input differs'
            for field in ('x','y','vx','vy','health'):
                a=value(native,'snes',field);b=value(other,'md',field)
                if field in ('x','y'):
                    a-=value(rows[15],'snes',field);b-=value(md[name][15],'md',field)
                if a!=b:differences.setdefault(field,[]).append({'frame':index,'snes':a,'md':b})
            if native['roar']!=other['roar']:roar.append(index)
        report['cases'][name]={'movement_health_differences':differences,'raw_roar_different_frames':roar}
        assert not differences,(name,differences)
        print(name,'fixed-point motion/velocity and health PASS',flush=True)
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
