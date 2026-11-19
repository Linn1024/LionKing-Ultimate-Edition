"""Compare original MD core samples to BizHawk by controller-read index.

Position/camera/health equivalence and roar counter observations are separate.
This does not certify full WRAM, rendering or complete movie synchronization.
"""
import argparse
import csv
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--replay',type=Path,required=True)
    args=ap.parse_args()
    replay=json.loads((args.replay/'frames.json').read_text())
    by_poll={r['poll']:r for r in replay if r['level']==0 and r.get('player_words')}
    count=0;poll=0;differences=[];roar=[]
    with args.reference.open() as stream:
        for row in csv.DictReader(stream):
            if row['lag']!='0':continue
            poll+=1
            if row['collision']!='27DA40' or poll not in by_poll:continue
            sample=by_poll[poll];count+=1
            expected={'player':[int(row['player_x']),int(row['player_y'])],
                      'camera':[int(row['camera_x']),int(row['camera_y'])],
                      'health':int(row['health'])}
            for field,value in expected.items():
                if sample[field]!=value:
                    differences.append({'poll':poll,'field':field,'expected':value,'actual':sample[field]})
            if sample['roar']!=int(row['roar']):
                roar.append({'poll':poll,'expected':int(row['roar']),'actual':sample['roar']})
    report={'scope':__doc__,'samples':count,'position_camera_health_differences':differences,
            'roar_charge_differences':roar,'full_wram_synchronization_verified':False}
    (args.replay/'reference-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    assert count>2000,'Insufficient Pride Lands reference coverage'
    assert not differences,str(differences[:10])
    print('Original MD motion/camera/health reference PASS:',count,'samples;',len(roar),'roar-charge observations differ')


if __name__=='__main__':main()
