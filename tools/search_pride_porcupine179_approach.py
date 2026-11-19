"""Preserve ordinary one-field approach shifts as separate native contact searches."""
import argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--shift',type=int,choices=(-1,1,2),required=True);args=ap.parse_args()
verifier_source=Path(__file__).with_name('capture_pride_porcupine177_difficulty.py')
source=verifier_source.read_text()
source=source.replace("ROOT/'build/pride-porcupine177-difficulty'","ROOT/'build/pride-porcupine179-shift"+str(args.shift)+"'")
source=source.replace('943<=int(row[0])<=1400',str(943+args.shift)+'<=int(row[0])<='+str(1400+args.shift))
source=source.replace('assert len(approach)==458 and approach[0]==0x100','assert len(approach)==458')
source=source.replace("[('easy',8),('normal',2),('hard',0)]","[('normal',2)]")
source=source.replace('all_three_have_attributed_porcupine_hits','normal_search_has_attributed_porcupine_hit')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
