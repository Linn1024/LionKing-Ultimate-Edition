/* Verified native queue/SPC/DSP ownership. Guest state is read-only.
 * Evidence and lifecycle contract: docs/pride-bounce-driver-lifecycle.md. */
#include "tlk_native_audio_owner.h"
#include "common_rtl.h"
#include "tlk_resources.h"
#include "tlk_md_sound.h"
#include "tlk_audio.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include "snes/interp_bridge.h"
static _Atomic unsigned s_sem_queue[84],s_sem_ring[64];
static unsigned s_sem_software[22],s_sem_candidate[8],s_sem_latched[8],s_sem_voice[8];
static unsigned s_sem_pending,s_sem_next;
/* High nibble identifies a verified request; low28 bits retain monotonic
 * transport identity. Bounce keeps kind0, menu calls have their own kinds. */
static unsigned SemKind(unsigned token) { return token>>28; }
static unsigned SemProgram(unsigned token) {
    unsigned kind=SemKind(token);
    return (kind==8 || kind==9 || kind==10)?41:(kind==0 || kind==11)?17:(kind==1 || kind==4 || kind==5 || kind==6)?5:6;
}
static unsigned SemNewToken(unsigned kind) {
    return s_sem_next>=0x0fffffff?0:(kind<<28)|++s_sem_next;
}
static int s_sem_driver_valid;
/* Original driver group E0 identifies music; 100 is unknown. Track actual
 * KON ownership, since a software slot may be reused while a voice decays. */
static unsigned s_music_candidate[8],s_music_latched[8],s_music_voice[8];
static FILE *s_sem_log;
static unsigned SemWord(const uint8_t *ram,unsigned at) {
    return ram[at]|(unsigned)ram[at+1]<<8;
}
static unsigned SemAddress(unsigned at) {
    return SemWord(g_ram,at)|(unsigned)g_ram[(at+2)&65535]<<16;
}
static void SemTrace(const char *stage,unsigned token,unsigned a,unsigned b) {
    const char *path=getenv("TLK_SEMANTIC_OWNER_TRACE");if(!path)return;
    if(!s_sem_log) {
        s_sem_log=fopen(path,"w");if(!s_sem_log)exit(96);
        fputs("field,stage,token,a,b\n",s_sem_log);
    }
    fprintf(s_sem_log,"%u,%s,%u,%u,%u\n",(unsigned)snes_frame_counter+1,stage,token,a,b);
}
static void OwnerClear(void) {
    for(unsigned i=0;i<84;i++)atomic_store(&s_sem_queue[i],0);
    for(unsigned i=0;i<64;i++)atomic_store(&s_sem_ring[i],0);
    memset(s_sem_software,0,sizeof s_sem_software);
    memset(s_sem_candidate,0,sizeof s_sem_candidate);
    memset(s_sem_latched,0,sizeof s_sem_latched);
    memset(s_sem_voice,0,sizeof s_sem_voice);
    s_sem_pending=0;
    /* Software transport invalidation does not stop already sounding voices
     * or cancel a KON already latched by the DSP. Unknown future KON writes
     * cannot acquire those owners. */
    for(unsigned i=0;i<8;i++)s_music_candidate[i]=0x100;
}
static unsigned SemStackAddress(unsigned at) { return g_ram[at&65535]|(unsigned)g_ram[(at+1)&65535]<<8|(unsigned)g_ram[(at+2)&65535]<<16; }
static int RollingRumbleEntry(const CpuState *cpu) {
    unsigned actor=SemWord(g_ram,0x68),scene=SemAddress(0xdf);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127))return 0;
    unsigned descriptor=SemAddress(actor+4),action=SemAddress(actor+48);
    unsigned caller=SemStackAddress(cpu->S+17)+1;
    if(scene==0xc0044f && SemWord(g_ram,0x1ff9e)==4)
        return descriptor==0xc58cb0 && action==0xc1678f && caller==0xc1684a &&
            SemWord(g_ram,actor+44)==40 && SemWord(g_ram,actor+46)==0xffff;
    return scene==0xc004e5 && SemWord(g_ram,0x1ff9e)==7 && descriptor==0xc58909 &&
        action==0xc06be0 && (caller==0xc06ca5 || caller==0xc06d07);
}
static void SemAccepted(CpuState *cpu,uint32_t pc) {
    SemTrace("queue_probe",0,cpu->D,cpu->m_flag);
    if(cpu->D!=0x1f00 || cpu->DB!=0x7e || !cpu->m_flag || cpu->x_flag ||
       cpu->X>=0x4c || cpu->X!=SemWord(g_ram,0x1f6d))return;
    unsigned cursor=cpu->X,token=0;
    for(unsigned i=0;i<8;i++)atomic_store(&s_sem_queue[cursor+i],0);
    if(SemWord(g_ram,0x1f15)==0x8011 && !SemWord(g_ram,0x1ff9e) &&
       !SemWord(g_ram,0x2000) && SemWord(g_ram,0x68)==0xb213 &&
       SemAddress(0xb217)==0xc5858a &&
       (SemAddress(0xdf)==0xc00387 || SemAddress(0xdf)==0xc0080d) &&
       SemStackAddress(cpu->S+17)+1==0xc36686)token=SemNewToken(0);
    /* Program17 has no volume argument. Adult landing is a separate source
     * from cub bounce and the NPC caller; retain its accepted-request identity
     * through the existing driver/KON path instead of changing guest audio. */
    unsigned level=SemWord(g_ram,0x1ff9e),scene=SemAddress(0xdf);
    if(SemWord(g_ram,0x1f15)==0x8011 && level>=6 && level<=9 &&
       SemWord(g_ram,0x2000)==0xffff && SemWord(g_ram,0x68)==0xb213 &&
       SemWord(g_ram,0x6e)==0xb213 && SemAddress(0xb217)==0xc5858a &&
       SemAddress(0xb243)==0xc362ec &&
       (scene==0xc00387+level*50 || (level==9 && scene==0xc007db)) &&
       SemStackAddress(cpu->S+17)+1==0xc36369)token=SemNewToken(11);
    if(SemAddress(0xdf)==0xc005ab) {
        unsigned caller=SemStackAddress(cpu->S+17)+1,event=SemWord(g_ram,0x1f15);
        if(event==0x8005 && (caller==0xc46849 || caller==0xc468a2))token=SemNewToken(1);
        else if(event==0x8006 && (caller==0xc467cf || caller==0xc46804))token=SemNewToken(2);
        else if(event==0x8006 && caller==0xc46a56)token=SemNewToken(3);
        else if(event==0x8005 && (caller==0xc46ace || caller==0xc46b25))token=SemNewToken(5);
        else if(event==0x8005 && caller==0xc469db)token=SemNewToken(4);
        unsigned actor=SemWord(g_ram,0x68);
        if(actor>=0x2000 && actor<=0xffa0 && actor==SemWord(g_ram,0x6e) &&
           SemAddress(actor+48)==0xc46e59) {
            /* Native programs5/6 remain queued and scheduled normally. Only
             * these accepted debug-menu voices gain the new output owner. */
            if(event==0x8005 && (caller==0xc46fba || caller==0xc47011 || caller==0xc46f12))token=SemNewToken(6);
            else if(event==0x8006 && caller==0xc46f42)token=SemNewToken(7);
        }
    }
    /* Original MD rolling stones omit native program41. Keep its complete
     * queue, volume ramps and stop scheduling; only its proven DSP voice gains
     * an output owner. Program41 in other callers (e.g. gorilla) is unrelated. */
    if(SemWord(g_ram,0x1f15)==0x8029 && RollingRumbleEntry(cpu))token=SemNewToken(8);
    if(SemWord(g_ram,0x1f15)==0x8029 && SemWord(g_ram,0x1ff9e)==6 &&
       SemAddress(0xdf)==0xc004b3 && SemWord(g_ram,0x2000)==0xffff){
        unsigned actor=SemWord(g_ram,0x68),caller=SemStackAddress(cpu->S+17)+1;
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           (SemAddress(actor+4)==0xc588dd || SemAddress(actor+4)==0xc588fd) &&
           SemAddress(actor+48)==0xc59015 && (caller==0xc59182 || caller==0xc591d5))token=SemNewToken(9);
    }
    if(SemWord(g_ram,0x1f15)==0x8029 && SemWord(g_ram,0x1ff9e)==7 &&
       SemAddress(0xdf)==0xc004e5 && SemWord(g_ram,0x2000)==0xffff){
        unsigned actor=SemWord(g_ram,0x68),caller=SemStackAddress(cpu->S+17)+1;
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           ((SemAddress(actor+4)==0xc58d52 && SemAddress(actor+48)==0xc2d4e4 && caller==0xc2d567) ||
            (SemAddress(actor+4)==0xc5874a && SemAddress(actor+48)==0xc2d8cc && caller==0xc2d997)))
            token=SemNewToken(10);
    }
    atomic_store(&s_sem_queue[cursor],token);
    if(token)SemTrace("accepted",token,cursor,0);
}
static void SemTransfer(CpuState *cpu,uint32_t pc) {
    if(cpu->D!=0x1f00 || cpu->m_flag || cpu->x_flag || cpu->X>=84 ||
       cpu->Y<0x204 || cpu->Y>=0x244 || (cpu->X&1) || (cpu->Y&1))return;
    unsigned token=atomic_exchange(&s_sem_queue[cpu->X],0);
    if(SemWord(g_ram,0x1f6f+cpu->X)!=(SemProgram(token)<<8|2))token=0;
    atomic_store(&s_sem_ring[cpu->Y-0x204],token);
    if(token)SemTrace("transfer",token,cpu->X,cpu->Y);
}
/* Called at original SPC instruction boundaries, before guest execution. */
static void OwnerSpc(unsigned pc,unsigned a,unsigned x,unsigned y,const uint8_t *ram) {
    if(pc==0x1bcb && !memcmp(ram+pc,"\xf6\x04\x02\x1c\x5d",5))s_sem_pending=0;
    if(pc==0x1be3 && !memcmp(ram+pc,"\xeb\xeb\xf6\x05\x02",5)) {
        s_sem_pending=0;
        if(y<64) {
            unsigned token=atomic_exchange(&s_sem_ring[y],0);
            if(ram[8]==SemProgram(token) && ram[0x204+y]==2 && ram[0x205+y]==SemProgram(token))
                s_sem_pending=token;
            if(s_sem_pending)SemTrace("dispatch",s_sem_pending,y,SemProgram(token));
        }
    }
    /* Programs5/6 skip the later FD1 metadata store. FC9 is the shared
     * initialization point observed in the original driver, before that branch. */
    if((pc==0x0fc9 && !memcmp(ram+pc,"\xd5\xe3\x02\x53\x32\x28",6)) ||
       (pc==0x0fd1 && s_sem_pending && SemProgram(s_sem_pending)==17 &&
        !memcmp(ram+pc,"\xd5\x51\x03\xd5\xa9\x03",6))) {
        if(x<22) {
            unsigned stream=SemWord(ram,0x294);
            /* Only the verified one-channel programs acquire an owner. */
            unsigned valid=stream>=15 && ram[stream-13]==SemProgram(s_sem_pending) && ram[stream-12]==1;
            s_sem_software[x]=valid?s_sem_pending:0;
            if(s_sem_software[x])SemTrace("software",s_sem_software[x],x,stream);
        }
        s_sem_pending=0;
    }
    if(pc==0x0d34 && !memcmp(ram+pc,"\xd5\x27\x05",3) && x<8) {
        s_music_candidate[x]=a<22?ram[0x2e3+a]:0x100;
        s_sem_candidate[x]=a<22?s_sem_software[a]:0;
        if(s_sem_candidate[x])SemTrace("assigned",s_sem_candidate[x],x,a);
    }
}
void TlkNativeAudioOwnerLatchKon(unsigned value) {
    for(unsigned ch=0;ch<8;ch++)s_music_latched[ch]=(s_sem_driver_valid && (value&(1u<<ch)))?s_music_candidate[ch]:0x100;
    for(unsigned ch=0;ch<8;ch++)s_sem_latched[ch]=(value&(1u<<ch))?s_sem_candidate[ch]:0;
}
void TlkNativeAudioOwnerCommit(unsigned ch) {
    if(ch<8) {
        s_sem_voice[ch]=s_sem_latched[ch];
        s_music_voice[ch]=s_music_latched[ch];
        if(s_sem_voice[ch])SemTrace("keyon",s_sem_voice[ch],ch,0);
    }
}
static int OwnerVoice(unsigned ch) { return ch<8 && s_sem_voice[ch]!=0; }
static void SemHooks(void) {
    interp_bridge_add_pre_opcode_hook(0xc21c90,SemAccepted);
    interp_bridge_add_pre_opcode_hook(0xc2212e,SemTransfer);
}

/* Private driver identity and transport invalidation, based on original traces. */
#include "sha256.h"
#include "snes/snes.h"
#include "snes/apu.h"
extern Snes *g_snes;
static int SemDriverCheck(const uint8_t *ram) {
    static const uint8_t expected[32]={
        0xdc,0xe6,0x8c,0x13,0x2e,0x0d,0x7c,0x29,0xa8,0xa0,0x02,0x4f,0x73,0xfb,0xdb,0x6e,
        0x3c,0x5b,0x5e,0x64,0x71,0xe4,0x59,0xdc,0xc7,0x36,0xaa,0xb4,0xc7,0xeb,0xf5,0x1f};
    if(!ram)return 0;
    uint8_t code[0x1800],hash[32];memcpy(code,ram+0x600,sizeof code);
    const unsigned operands[]={0x1a76,0x1a77,0x1a7f,0x1a80};
    for(unsigned i=0;i<4;i++)code[operands[i]-0x600]=0;
    sha256_compute(code,sizeof code,hash);return !memcmp(hash,expected,32);
}
void TlkNativeAudioOwnerReset(void) {
    s_sem_driver_valid=0;OwnerClear();
    for(unsigned i=0;i<8;i++)s_music_latched[i]=s_music_voice[i]=0x100;
}
static void SemDriverValidate(const uint8_t *ram) {
    s_sem_driver_valid=SemDriverCheck(ram);
    if(!s_sem_driver_valid)OwnerClear();
}
void TlkNativeAudioOwnerSpc(unsigned pc,unsigned a,unsigned x,unsigned y,const uint8_t *ram) {
    if(pc==0x1bcb || pc==0x1be3 || pc==0xfc9 || pc==0xfd1 || pc==0xd34)SemDriverValidate(ram);
    if(s_sem_driver_valid)OwnerSpc(pc,a,x,y,ram);
}
static int OwnerVerifiedVoice(unsigned ch) {
    return s_sem_driver_valid && OwnerVoice(ch);
}
static void SemDriverCpu(CpuState *cpu,uint32_t pc) {
    pc|=0x800000;
    if(cpu->D!=0x1f00 || !cpu->m_flag)return;
    if((pc==0xc21ebf && !cpu->x_flag) || (pc==0xc21955 && cpu->x_flag)) {
        /* A CPU-side driver reboot precedes the hardware reset/upload. Keep
         * ownership of its audible tail and already latched hardware KON. */
        s_sem_driver_valid=0;OwnerClear();SemTrace("driver_reset",0,pc,0);
    } else if(pc==0xc21e15 && !cpu->x_flag && !cpu->DB) {
        /* All queued words were transferred. Ring/software/voice owners survive. */
        for(unsigned i=0;i<84;i++)atomic_store(&s_sem_queue[i],0);
        SemTrace("queue_drained",0,pc,0);
    } else if(pc==0xc22349 && !cpu->x_flag && !cpu->DB) {
        SemDriverValidate(g_snes && g_snes->apu?g_snes->apu->ram:NULL);
        SemTrace("upload_checked",0,pc,s_sem_driver_valid);
    }
}
static void SemDriverHooks(void) {
    const unsigned pcs[]={0xc21ebf,0xc21955,0xc21e15,0xc22349};
    for(unsigned i=0;i<4;i++)interp_bridge_add_pre_opcode_hook(pcs[i],SemDriverCpu);
}

/* Versioned, endian-stable private native ownership continuation. */
enum { SEMANTIC_TOKEN_END=800, SEMANTIC_STATE_SIZE=896 };
static unsigned SemGet32(const uint8_t *p) {
    return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;
}
static void SemPut32(uint8_t *p,unsigned v) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));
}
size_t TlkNativeAudioOwnerStateSize(void) { return SEMANTIC_STATE_SIZE; }
int TlkNativeAudioOwnerValidate(const uint8_t *data,size_t size) {
    if(!data || size!=SEMANTIC_STATE_SIZE || memcmp(data,"SEMOWN03",8) ||
       SemGet32(data+8)!=3 || SemGet32(data+12)!=size)return 0;
    unsigned next=SemGet32(data+16);
    if(next>0x0fffffff)return 0;
    for(unsigned at=20;at<SEMANTIC_TOKEN_END;at+=4) {
        unsigned token=SemGet32(data+at),serial=token&0x0fffffff;
        if(SemKind(token)>11 || serial>next || (token && !serial))return 0;
    }
    for(unsigned at=SEMANTIC_TOKEN_END;at<size;at+=4) {
        unsigned group=SemGet32(data+at);
        if(group>0x100)return 0;
    }
    return 1;
}
int TlkNativeAudioOwnerSave(uint8_t *data,size_t size) {
    if(!data || size!=SEMANTIC_STATE_SIZE)return 0;
    memset(data,0,size);memcpy(data,"SEMOWN03",8);
    SemPut32(data+8,3);SemPut32(data+12,size);
    SemPut32(data+16,s_sem_next);SemPut32(data+20,s_sem_pending);
    unsigned at=24;
    for(unsigned i=0;i<84;i++,at+=4)SemPut32(data+at,atomic_load(&s_sem_queue[i]));
    for(unsigned i=0;i<64;i++,at+=4)SemPut32(data+at,atomic_load(&s_sem_ring[i]));
    const unsigned *arrays[]={s_sem_software,s_sem_candidate,s_sem_latched,s_sem_voice};
    const unsigned counts[]={22,8,8,8};
    for(unsigned n=0;n<4;n++)for(unsigned i=0;i<counts[n];i++,at+=4)SemPut32(data+at,arrays[n][i]);
    const unsigned *music[]={s_music_candidate,s_music_latched,s_music_voice};
    for(unsigned n=0;n<3;n++)for(unsigned i=0;i<8;i++,at+=4)SemPut32(data+at,music[n][i]);
    return at==size && TlkNativeAudioOwnerValidate(data,size);
}
static int OwnerLoadState(const uint8_t *data,size_t size) {
    if(!TlkNativeAudioOwnerValidate(data,size))return 0;
    s_sem_next=SemGet32(data+16);s_sem_pending=SemGet32(data+20);
    unsigned at=24;
    for(unsigned i=0;i<84;i++,at+=4)atomic_store(&s_sem_queue[i],SemGet32(data+at));
    for(unsigned i=0;i<64;i++,at+=4)atomic_store(&s_sem_ring[i],SemGet32(data+at));
    unsigned *arrays[]={s_sem_software,s_sem_candidate,s_sem_latched,s_sem_voice};
    const unsigned counts[]={22,8,8,8};
    for(unsigned n=0;n<4;n++)for(unsigned i=0;i<counts[n];i++,at+=4)arrays[n][i]=SemGet32(data+at);
    unsigned *music[]={s_music_candidate,s_music_latched,s_music_voice};
    for(unsigned n=0;n<3;n++)for(unsigned i=0;i<8;i++,at+=4)music[n][i]=SemGet32(data+at);
    return 1;
}


void TlkNativeAudioOwnerInstall(void) { SemHooks();SemDriverHooks(); }
void TlkNativeAudioOwnerCpu(CpuState *cpu,uint32_t pc) {
    pc|=0x800000;
    if(pc==0xc21c90)SemAccepted(cpu,pc);
    else if(pc==0xc2212e)SemTransfer(cpu,pc);
    else SemDriverCpu(cpu,pc);
}
int TlkNativeAudioOwnerLoad(const uint8_t *data,size_t size) {
    if(!OwnerLoadState(data,size))return 0;
    SemDriverValidate(g_snes && g_snes->apu?g_snes->apu->ram:NULL);
    /* Restoring unknown code cannot establish a new trusted voice history. */
    if(!s_sem_driver_valid)for(unsigned i=0;i<8;i++)s_music_latched[i]=s_music_voice[i]=0x100;
    return 1;
}
int TlkNativeAudioOwnerMute(unsigned channel,unsigned srcn,int echo) {
    if(!OwnerVerifiedVoice(channel) || echo)return 0;
    unsigned scene=SemAddress(0xdf);
    unsigned kind=SemKind(s_sem_voice[channel]);
    if(kind==8)return TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.world.rolling_stones");
    if(kind==9)return TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.world.simbas_destiny.boulders");
    if(kind==10)return TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.world.be_prepared.geysers");
    if(kind==11)return srcn==92 && TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.simba.adult_landing");
    if(kind) {
        static const char *ids[]={"","audio.effects.title_cursor","audio.effects.title_selection",
            "audio.effects.options_adjustment","audio.effects.options_exit","audio.effects.options_cursor",
            "audio.effects.level_select","audio.effects.level_select"};
        return kind<=7 && scene==0xc005ab &&
            /* An accepted menu request can turn effects off immediately.
             * Its already sounding native voice still belongs to that request. */
            TlkMdSoundReady() && TlkResourcesUseMd(ids[kind]);
    }
    if(srcn!=92)return 0;
    return !SemWord(g_ram,0x1ff9e) && !SemWord(g_ram,0x2000) &&
        (scene==0xc00387 || scene==0xc0080d) && SemWord(g_ram,0x1ff96) &&
        TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.simba.bounce");
}
int TlkNativeAudioOwnerMusicMute(unsigned channel,int echo_volume_l,int echo_volume_r) {
    return channel<8 && s_music_voice[channel]==0xe0 &&
        !echo_volume_l && !echo_volume_r && TlkAudioNativeMusicSelected();
}
