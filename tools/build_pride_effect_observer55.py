"""Add read-only latched-piece evidence to a private copy of preview53."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

OBSERVER=r'''
static void EffectCoverageFrame(void) {
    const char *path=getenv("TLK_EFFECT_LATCH_TRACE");if(!path || !*path)return;
    static FILE *log;static unsigned frames,pieces,mapped;
    if(!log){log=fopen(path,"w");if(!log)return;
        fputs("field,descriptor,stage,object,position,pose,slot,kept,fixed,x,y,size,palette,hud_role,title_role,oam_rows,lit_oam_rows,wide_candidate_rows,actor_descriptor,actor_action\n",log);}
    unsigned descriptor=rd16(s_frame.ram+0xdf);
    if(rd16(s_frame.ram+0x1ff9e) || (descriptor!=0x387 && descriptor!=0x80d))return;
    frames++;
    for(unsigned n=0;n<s_frame.piece_count;n++) {
        const Piece *p=&s_frame.pieces[n];int bx,by,bw,bh;pieces++;
        if(TlkMdSpritesBounds(p->pose,&bx,&by,&bw,&bh)){mapped++;continue;}
        unsigned oam_rows=0,lit_rows=0,wide_rows=0,idx=(p->slot&127)*2;
        for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
            const Line *l=&s_frame.lines[y];
            int lit=!(l->inidisp&0x80) && (l->inidisp&15) && ((l->tm|l->ts)&16);
            unsigned row=(y-(l->oam[idx]>>8))&255;
            if(p->kept && p->x==OamX(l,idx) && (p->y&255)==(l->oam[idx]>>8) &&
               p->size==OamSize(l,idx) && p->attr==l->oam[idx+1] && row<p->size &&
               p->x<256 && p->x+p->size>0) {oam_rows++;if(lit)lit_rows++;}
            /* Conservative possible wide-margin coverage; no pixel opacity,
             * OBJ limits or occlusion is inferred from this bounding test. */
            if(lit && ((y-(unsigned)p->y)&255)<p->size && p->x<288 && p->x+p->size>-32)wide_rows++;
        }
        unsigned position=p->obj<=0xfffa?rd16(s_frame.ram+p->obj+4):0;
        unsigned actor=position>=0x8008 && position<=0xff88?position-8:0;
        fprintf(log,"%d,%04x,%u,%04x,%04x,%06x,%u,%u,%u,%d,%d,%u,%u,%d,%u,%u,%u,%u,%06x,%06x\n",
            snes_frame_counter,descriptor,s_frame.stage,p->obj,position,p->pose,p->slot,p->kept,p->fixed,
            p->x,p->y,p->size,(p->attr>>9)&7,HudMeter(p),TitlePiece(p),oam_rows,lit_rows,wide_rows,
            actor?rd24(s_frame.ram+actor+4):0,actor?rd24(s_frame.ram+actor+0x30):0);
    }
    fflush(log);
    const char *summary=getenv("TLK_EFFECT_LATCH_SUMMARY");
    if(summary && *summary){FILE *f=fopen(summary,"w");if(f){fprintf(f,"{\"frames\":%u,\"pieces\":%u,\"mapped\":%u}\n",frames,pieces,mapped);fclose(f);}}
}
'''


def main():
    base=ROOT/'build/pride-checkpoint-capability53';buildpath=base/'build-report.json';build=bound(buildpath)
    widepath=ROOT/'build/pride-continue-token46/build-report.json';wide=bound(widepath)
    out=ROOT/'build/pride-effect-observer56';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    cmd=wide['compiles']['wide'].copy();cmd[cmd.index('-c')]='-E';cmd.append('-P')
    for flag,value in [('-o',out/'original.i'),('-MT',out/'observer.obj'),('-MF',out/'preprocess.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    text=(out/'original.i').read_text();anchor='_Bool TlkWideEndFrame(const uint8_t *stock) {'
    assert text.count(anchor)==1
    text=text.replace(anchor,OBSERVER+'\n'+anchor)
    anchor='return s_frame.valid = 1;'
    assert text.count(anchor)==1
    text=text.replace(anchor,'s_frame.valid = 1; EffectCoverageFrame(); return 1;')
    source=out/'observer.i';source.write_text(text)
    compilecmd=wide['compiles']['wide'].copy()
    for flag,value in [('-c',source),('-o',out/'observer.obj'),('-MT',out/'observer.obj'),('-MF',out/'observer.d')]:compilecmd[compilecmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(compilecmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:]
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==ROOT/'build/pride-continue-token46/wide.obj']
    assert len(indices)==1;inputs[indices[0]]=(out/'observer.obj').as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(base/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(build['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==321 and len(linked)==322
    paths=[Path(__file__),buildpath,widepath,source,out/'original.i',rsp,ROOT/'engine/runner/tlk_wide.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),preprocess=cmd,compile=compilecmd,
                link_inputs_sha256=linked,unchanged_inputs=unchanged,observer_only=True,guest_or_rom_writes_added=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
