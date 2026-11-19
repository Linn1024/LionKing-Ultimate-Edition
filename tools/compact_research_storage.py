"""Lossless Windows compression of research output, with before/after hashes.

Only visits real files below ignored build/. Never follows links or removes
files. Source, ROMs, installed data, saves outside build and submodules excluded.
"""
import argparse
import concurrent.futures
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
K=C.WinDLL('kernel32',use_last_error=True)
K.GetCompressedFileSizeW.argtypes=[C.c_wchar_p,C.POINTER(C.c_ulong)]
K.GetCompressedFileSizeW.restype=C.c_ulong
def allocated(path):
    high=C.c_ulong();C.set_last_error(0)
    low=K.GetCompressedFileSizeW(str(path),C.byref(high))
    if low==0xffffffff and C.get_last_error():raise C.WinError(C.get_last_error())
    return low+(high.value<<32)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(4*1024*1024),b''):h.update(data)
    return h.hexdigest()
def candidates(build,extensions,minimum,excluded):
    stack=[build]
    while stack:
        folder=stack.pop()
        with os.scandir(folder) as entries:
            for entry in entries:
                path=Path(entry.path)
                if entry.is_symlink() or os.path.isjunction(entry.path) or path==excluded:continue
                if entry.is_dir(follow_symlinks=False):stack.append(path)
                elif entry.is_file(follow_symlinks=False) and path.suffix.lower() in extensions:
                    size=entry.stat(follow_symlinks=False).st_size
                    if size<minimum:continue
                    physical=allocated(path)
                    if physical>size//10:yield dict(path=path.relative_to(ROOT).as_posix(),logical=size,allocated=physical)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--extensions',nargs='+',default=['.rgb'])
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--minimum-mib',type=int,default=16)
    args=ap.parse_args();build=(ROOT/'build').resolve();out=(ROOT/args.output).resolve()
    assert out.is_relative_to(build) and out!=build
    out.mkdir();start=time.monotonic();free_before=shutil.disk_usage(ROOT).free
    rows=sorted(candidates(build,set(args.extensions),args.minimum_mib*1024**2,out),key=lambda r:r['allocated'],reverse=True)
    (out/'inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Candidates',len(rows),'allocated GiB',round(sum(r['allocated'] for r in rows)/2**30,2),flush=True)
    results=[]
    def run(row):
        p=(ROOT/row['path']).resolve();assert p.is_relative_to(build) and p.is_file() and not p.is_symlink() and not os.path.isjunction(p)
        if shutil.disk_usage(ROOT).free<512*1024**2:raise RuntimeError('Less than512MiB headroom; do not risk compaction')
        before_sha=sha(p);before=allocated(p)
        r=subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(p)],capture_output=True,text=True,errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
        after_sha=sha(p);after=allocated(p)
        result=dict(path=row['path'],logical=p.stat().st_size,allocated_before=before,allocated_after=after,
                    sha256_before=before_sha,sha256_after=after_sha,bytes_unchanged=before_sha==after_sha,exit=r.returncode,
                    output=r.stdout,stderr=r.stderr)
        if before_sha!=after_sha:raise RuntimeError('File contents changed: '+str(p))
        return result
    if args.apply:
        with (out/'files.jsonl').open('x',encoding='utf-8') as journal:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures=[pool.submit(run,row) for row in rows]
                for future in concurrent.futures.as_completed(futures):
                    row=future.result();results.append(row);journal.write(json.dumps(row)+'\n');journal.flush()
                    if len(results)%20==0 or len(results)==len(rows):
                        progress=dict(completed=len(results),total=len(rows),saved_allocated_bytes=sum(r['allocated_before']-r['allocated_after'] for r in results),free_bytes=shutil.disk_usage(ROOT).free)
                        (out/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
                        print('Verified',len(results),'/',len(rows),'saved GiB',round(progress['saved_allocated_bytes']/2**30,2),flush=True)
    report=dict(result='PASS' if args.apply and all(r['bytes_unchanged'] and r['exit']==0 for r in results) else 'AUDITED' if not args.apply else 'PARTIAL',
        candidate_count=len(rows),verified_files=len(results),allocated_saved_bytes=sum(r['allocated_before']-r['allocated_after'] for r in results),
        free_before=free_before,free_after=shutil.disk_usage(ROOT).free,seconds=time.monotonic()-start,
        file_deletions=0,scope='Transparent Windows LZX compression under ignored build only; every processed file checked with SHA256 before/after. All paths and logical bytes preserved.',
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
