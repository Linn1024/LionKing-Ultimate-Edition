/* Opt-in starting health for private recording preparation only. No setting,
 * ROM patch or per-level gameplay rule is changed by ordinary launches. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern uint8_t g_ram[0x20000];
void __real_TlkAudioFrame(unsigned field);
static unsigned word(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned address(unsigned at){return word(at)|(unsigned)g_ram[at+2]<<16;}
static void put(unsigned at,unsigned value){g_ram[at]=(uint8_t)value;g_ram[at+1]=(uint8_t)(value>>8);}
/* Fresh-level showcase starts: collect the earlier permanent health upgrades
 * in Pride Lands, Graveyard, Hakuna and Return (+2 each). The current level's
 * upgrade remains available to collect. Excludes optional bonus farming. */
static const unsigned starting_health[10]={4,6,6,0,8,8,10,10,10,12};
void __wrap_TlkAudioFrame(unsigned field){
    static int checked,enabled,applied;
    static unsigned apply_at;
    if(!checked){
        checked=1;const char *flag=getenv("TLK_RECORD_START_MAX_HEALTH"),*at=getenv("TLK_RECORD_HEALTH_AT");
        enabled=flag&&!strcmp(flag,"1");apply_at=at?(unsigned)strtoul(at,NULL,10):1700;
    }
    if(enabled&&!applied&&field>=apply_at){
        unsigned level=word(0x1ff9e),age=word(0x2000),hp=word(0x2004),maximum=word(0x1ffac);
        if(level<=9&&level!=3&&address(0xdf)==0xc00387+level*50&&
           age==(level>=6?65535u:0u)&&hp&&hp<=maximum&&maximum>=4&&maximum<=12&&
           address(0xb217)==0xc5858a&&!word(0xa6ba)&&address(0xb243)){
            /* Original C00228 clamps the health capacity to4..12. Roar
             * capacity is the separate1FFAE word and is left unchanged. */
            unsigned target=starting_health[level];
            put(0x1ffac,target);put(0x2004,target);applied=1;
            fprintf(stderr,"recording_start_health field=%u level=%u old_max=%u old_hp=%u max=%u hp=%u\n",field,level,maximum,hp,target,target);
        }
    }
    __real_TlkAudioFrame(field);
}
