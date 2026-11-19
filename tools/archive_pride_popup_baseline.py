"""Retain exact pre-popup maintained sources for frozen earlier evidence."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-popup-baseline'
    out.mkdir()
    names=['engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c',
           'engine/runner/tlk_md_sprites.h','engine/runner/tlk_resources.c',
           'tools/pride_sprite_catalog.py','tools/pride_npc_pairs.json']
    rows={}
    for name in names:
        dest=out/'sources'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,dest)
        rows[name]=dict(sha256=digest(dest),archive=dest.relative_to(ROOT).as_posix())
    (out/'report.json').write_text(json.dumps(dict(result='ARCHIVED',historical_sources=rows),indent=2)+'\n')
    print('Archived',len(rows),'pre-popup sources',flush=True)


if __name__=='__main__':main()
