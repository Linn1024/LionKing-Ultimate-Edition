"""Build a field-level read-only actor observer around the qualified player44."""
from pathlib import Path

OBSERVER = r'''
static unsigned WalkWord(unsigned at){return g_ram[at]|g_ram[at+1]<<8;}
static unsigned WalkPointer(unsigned at){return WalkWord(at)|g_ram[at+2]<<16;}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    _Bool result=CacheObservedFinalRunFrame(inputs);
    const char *path=getenv("TLK_WALK_ACTOR_LOG");
    if(path && *path){
        static FILE *log;
        if(!log){log=fopen(path,"w");if(!log)exit(96);
            fputs("field,actor,action,animation,timer,wait,persistent,x,y,player_x,player_y,player_action,strength,health,flags\n",log);}
        for(unsigned actor=0xb213;actor<=0xc193;actor+=128){
            if(actor!=0xb213 && WalkPointer(actor+4)!=0xc58c5c)continue;
            fprintf(log,"%u,%04x,%06x,%06x,%u,%u,%u,%u,%u,%u,%u,%06x,%u,%u,%u\n",
                (unsigned)snes_frame_counter,actor,WalkPointer(actor+0x30),WalkPointer(actor+0xe),
                WalkWord(actor+0x2c),WalkWord(actor+0x1c),WalkWord(actor+0x22),WalkWord(actor+8),WalkWord(actor+10),
                WalkWord(0xb21b),WalkWord(0xb21d),WalkPointer(0xb243),WalkWord(0xa698),WalkWord(0x2004),g_ram[0xb256]);
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
source = source.replace(before, "source = original.read_text().replace('from build_pride_rng_allbugs import OBSERVER', '').replace(\"out = base/'allbugs-observer'\", \"out = base/'walking-observer'\")")
exec(compile(source, str(previous), 'exec'))
