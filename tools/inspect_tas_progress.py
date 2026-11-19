"""Read the latest complete record from a running compressed TAS diagnostic stream."""
import argparse,json,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('path',type=Path);args=p.parse_args()
decoder=zlib.decompressobj(31);pending=b'';last=None;rows=0
with args.path.open('rb')as f:
    while block:=f.read(65536):
        lines=(pending+decoder.decompress(block)).split(b'\n');pending=lines.pop()
        complete=[line for line in lines if line]
        if complete:last=complete[-1];rows+=len(complete)
if last is None:print('No complete progress record yet')
else:
    r=json.loads(last);print(json.dumps(dict(rows=rows,**{k:r[k]for k in ['field','level','descriptor','health','lives','difficulty','control_layout','poll_index']})))
