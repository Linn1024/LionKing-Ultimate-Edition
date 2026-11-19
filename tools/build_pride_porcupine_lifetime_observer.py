"""Build a active-list read-only porcupine observer around the qualified player44."""
from pathlib import Path

OBSERVER = r'''

static unsigned WalkWord(unsigned at){return g_ram[at]|g_ram[at+1]<<8;}
static unsigned WalkPointer(unsigned at){return WalkWord(at)|g_ram[at+2]<<16;}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    _Bool result=CacheObservedFinalRunFrame(inputs);
    const char *path=getenv("TLK_PORCUPINE_LIFETIME_LOG");
    if(path && *path){
        static FILE *log;
        if(!log){log=fopen(path,"w");if(!log)exit(96);
            fputs("field,actor,previous,next,action,animation,timer,wait,persistent,x,y,facing,attribute,player_x,player_y,health,level,descriptor\n",log);}
        unsigned descriptor=WalkPointer(0xdf);
        if(!WalkWord(0x1ff9e) && (descriptor==0xc00387 || descriptor==0xc0080d)){
            unsigned previous=0,count=0;
            for(unsigned actor=WalkWord(0x76);actor;actor=WalkWord(actor+2)){
                if(actor<0x8000 || actor>0xff80 || count++>=80 || WalkWord(actor)!=previous){
                    fputs("INVALID_ACTIVE_LIST\n",log);fflush(log);exit(96);
                }
                if(WalkPointer(actor+4)==0xc58c5c){
                    fprintf(log,"%u,%04x,%04x,%04x,%06x,%06x,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%06x\n",
                        (unsigned)snes_frame_counter,actor,previous,WalkWord(actor+2),WalkPointer(actor+0x30),WalkPointer(actor+0xe),
                        WalkWord(actor+0x2c),WalkWord(actor+0x1c),WalkWord(actor+0x22),WalkWord(actor+8),WalkWord(actor+10),
                        WalkWord(actor+0x20),g_ram[actor+0x40],WalkWord(0xb21b),WalkWord(0xb21d),WalkWord(0x2004),WalkWord(0x1ff9e),descriptor);
                }
                previous=actor;
            }
        }
        fflush(log);
    }
    return result;
}

'''

previous = Path(__file__).with_name('build_pride_sprite_allbugs.py')
source = previous.read_text()
# Reuse the reviewed compilation/link pipeline; retain every nonhost input.
before = "source = original.read_text()"
assert source.count(before) == 1
source = source.replace(before, "source = original.read_text().replace('from build_pride_rng_allbugs import OBSERVER', '').replace(\"out = base/'allbugs-observer'\", \"out = base/'porcupine-lifetime-observer'\")")
exec(compile(source, str(previous), 'exec'))
