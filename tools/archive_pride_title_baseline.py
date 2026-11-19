"""Preserve maintained pre-caption sources for frozen previous evidence."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-title-baseline';out.mkdir()
    names=['engine/runner/tlk_wide.c','engine/runner/tlk_resources.c','engine/runner/tlk_resources.h',
           'engine/runner/tlk_revival_art.c','engine/runner/tlk_revival_art.h','engine/CMakeLists.txt']
    rows={}
    for name in names:
        target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
        rows[name]=dict(sha256=digest(target),archive=target.relative_to(ROOT).as_posix())
    (out/'report.json').write_text(json.dumps(dict(result='ARCHIVED',historical_sources=rows),indent=2)+'\n')
    print('Archived',len(rows),'pre-caption sources')


if __name__=='__main__':main()
