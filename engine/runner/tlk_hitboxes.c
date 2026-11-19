#include "tlk_hitboxes.h"
#include "tlk_hitbox_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_guest.h"
#include "tlk_resources.h"
#include "tlk_graveyard_hyena_owner.h"
#include "tlk_late_scene_data.h"
#include "tlk_be_prepared_data.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
/* Post-instruction seams: retain original bus timing and all original stores.
 * These loads/arithmetic always follow original CLC or SEC respectively, so
 * their input accumulator can be recovered without any hidden host state. */
static const struct { unsigned pc,component,operation,enemy; } sites[]={
    {0xb486,0,0,0},{0xb495,2,1,0},{0xb4a3,0,2,0},{0xb4af,2,2,0},
    {0xb4bf,1,0,0},{0xb4ce,3,1,0},{0xb4dc,1,2,0},{0xb4e8,3,2,0},
    {0xd53c,0,0,1},{0xd54c,2,1,1},{0xd55b,0,2,1},{0xd568,2,2,1},
    {0xd58c,1,0,1},{0xd59c,3,1,1},{0xd5ab,1,2,1},{0xd5b8,3,2,1}
};
static unsigned word(unsigned p) { return g_ram[p]|(unsigned)g_ram[p+1]<<8; }
static unsigned pointer(unsigned p) { return word(p)|(unsigned)g_ram[p+2]<<16; }
/* C2EBCE follows the real C0CFEE point test in the rhino-tail idle action.
 * MD19CFEC calls MD18D484 here: its prepared pose rectangle and inclusive
 * comparisons differ from the native tail. Keep the original player probe,
 * actor action, cooldown and ownership; replace only this helper's result. */
void TlkTailContactPostOpcode(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc2ebce || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc2 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x26 ||
       !TlkResourcesUseMd("gameplay.levels.cant_wait.rhino_tail_bounds"))return;
    unsigned actor=word(0x68),draw,pose;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(actor+4)!=0xc58c08 || pointer(actor+48)!=0xc2ead2)return;
    draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
    pose=pointer(draw+10);int bounds[4];
    for(unsigned i=0;i<4;i++) {
        unsigned native,external;
        if(!TlkHitboxDataGet(pose,5,i,&native,&external))return;
        bounds[i]=(int16_t)external;
    }
    if(g_ram[draw+8]&64) {int left=bounds[0];bounds[0]=-bounds[2];bounds[2]=-left;}
    if(g_ram[draw+8]&128) {int top=bounds[1];bounds[1]=-bounds[3];bounds[3]=-top;}
    for(unsigned i=0;i<4;i++)bounds[i]=(int16_t)(word(actor+8+(i&1)*2)+bounds[i]);
    int x=(int16_t)word(cpu->D+0x24),y=(int16_t)word(cpu->D+0x22);
    unsigned result=(x>=bounds[0] && x<=bounds[2] && y>=bounds[1] && y<=bounds[3])?65535:0;
    static FILE *trace;static int initialized;
    if(!initialized) {const char *path=getenv("TLK_TAIL_CONTACT_TRACE");initialized=1;
        if(path)trace=fopen(path,"w");
        if(trace)fprintf(trace,"pc,actor,pose,x,y,left,top,right,bottom,native,md\n");}
    if(trace) {fprintf(trace,"%06x,%04x,%06x,%d,%d,%d,%d,%d,%d,%04x,%04x\n",
        pc,actor,pose,x,y,bounds[0],bounds[1],bounds[2],bounds[3],word(0xa68e),result);fflush(trace);}
    /* The original helper publishes both aliases, preserving registers/flags. */
    g_ram[0xa68e]=g_ram[0xa690]=(uint8_t)result;
    g_ram[0xa68f]=g_ram[0xa691]=(uint8_t)(result>>8);
}
/* MD18D594 inclusive AABB contact, independently selected body operands.
 * Called after the original helper and first argument PLA; retain all
 * original registers, flags, contact stores and rhino bounce decisions. */
static int rhino_rectangle(unsigned actor,unsigned family,int selected,int box[4]){
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return 0;
    unsigned pose=pointer(draw+10);
    for(unsigned i=0;i<4;i++){
        unsigned native,external;
        if(!TlkHitboxDataGet(pose,family,i,&native,&external))return 0;
        box[i]=(int16_t)(selected?external:native);
    }
    if(g_ram[draw+8]&64){int left=box[0];box[0]=-box[2];box[2]=-left;}
    if(g_ram[draw+8]&128){int top=box[1];box[1]=-box[3];box[3]=-top;}
    for(unsigned i=0;i<4;i++)box[i]=(int16_t)(word(actor+8+(i&1)*2)+box[i]);
    return 1;
}
static void rhino_contact(CpuState *cpu,uint32_t pc){
    if(pc!=0xc2e856 || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc2 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x22 || word(0x6e)!=0xb213)return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(actor+4)!=0xc58c14 || pointer(actor+48)!=0xc2e7f1 || pointer(0xb217)!=0xc5858a)return;
    int selected=TlkResourcesUseMd("gameplay.levels.cant_wait.rhino_bounds"),player_md=TlkResourcesUseMd("gameplay.hitboxes.simba");
    if(!selected && !player_md)return;
    int body[4],player[4];if(!rhino_rectangle(actor,6,selected,body) || !rhino_rectangle(0xb213,0,player_md,player))return;
    unsigned result=(body[2]>=player[0] && body[3]>=player[1] && body[0]<=player[2] && body[1]<=player[3])?65535:0;
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_RHINO_CONTACT_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,actor,body_pose,player_pose,body_left,body_top,body_right,body_bottom,player_left,player_top,player_right,player_bottom,native,result,body_md,player_md\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%06x,%06x,%d,%d,%d,%d,%d,%d,%d,%d,%04x,%04x,%d,%d\n",snes_frame_counter+1,actor,pointer(word(actor+12)+10),pointer(word(0xb21f)+10),body[0],body[1],body[2],body[3],player[0],player[1],player[2],player[3],word(0xa68e),result,selected,player_md);fflush(trace);}
    g_ram[0xa68e]=g_ram[0xa690]=(uint8_t)result;
    g_ram[0xa68f]=g_ram[0xa691]=(uint8_t)(result>>8);
}
extern void (*g_tlk_cw_rhino_pc_hook)(CpuState *,uint32_t);
static void rhino_after(CpuState *cpu,uint32_t pc){rhino_contact(cpu,pc+1);}
static void pre(CpuState *cpu,uint32_t pc) {
    int exile=word(0x1ff9e)==4 && pointer(0xdf)==0xc0044f;
    int graveyard=word(0x1ff9e)==2 && pointer(0xdf)==0xc003eb;
    int pride=!word(0x1ff9e) && (pointer(0xdf)==0xc00387 || pointer(0xdf)==0xc0080d);
    int cantwait=word(0x1ff9e)==1 && pointer(0xdf)==0xc003b9;
    int hakuna=word(0x1ff9e)==5 && pointer(0xdf)==0xc00481 && !word(0x2000);
    unsigned level=word(0x1ff9e);
    int adult_player=level>=6 && level<=9 && pointer(0xdf)==0xc004b3+(level-6)*50 && word(0x2000)==0xffff;
    int hunt=level>=11 && level<=13 && pointer(0xdf)==0xc0060f+(level-11)*50;
    int adult=((word(0x1ff9e)==7 && pointer(0xdf)==0xc004e5) ||
               (word(0x1ff9e)==8 && pointer(0xdf)==0xc00517) ||
               (word(0x1ff9e)==9 && pointer(0xdf)==0xc00549)) && word(0x2000)==0xffff;
    if((!pride && !exile && !graveyard && !adult && !cantwait && !hakuna && !hunt && !adult_player) || g_ram[0xe1]!=0xc0 ||
       cpu->D || cpu->DB!=0x7e || cpu->PB!=0xc0 || cpu->m_flag || cpu->_flag_D || !TlkHitboxDataReady())return;
    for(unsigned i=0;i<sizeof sites/sizeof sites[0];i++) {
        if((pc&65535)!=sites[i].pc)continue;
        unsigned enemy=sites[i].enemy,component=sites[i].component,op=sites[i].operation;
        if((graveyard || hunt || exile) && !enemy)return;
        if(adult_player && !adult && enemy)return;
        if(cantwait && enemy)return;
        if(cpu->x_flag!=!enemy || cpu->Y!=12+component*2)return;
        unsigned actor=word(enemy?0x68:0x6e),draw=word(0x7c),pose=pointer(enemy?0x99:0x0d);
        if(enemy ? actor<((graveyard || adult || hunt)?0xb293:0xb313) || actor>=((hunt || hakuna || adult)?0xdc13:0xc213) || ((actor-0xb213)&127) : actor!=0xb213)return;
        if(draw<0x8000 || draw>0xffe8 || word(actor+12)!=draw || pointer(draw+10)!=pose)return;
        if((cantwait || ((hakuna || adult_player) && !enemy)) && pointer(actor+4)!=0xc5858a)return;
        if(adult_player && !enemy && (word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40)))return;
        unsigned bounds_family=enemy,prepared=0;
        const char *choice=enemy?"gameplay.hitboxes.enemies":"gameplay.hitboxes.simba";
        if(exile){
            if(pointer(actor+4)!=0xc58cbc || word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
            choice="gameplay.levels.simbas_exile.falling_rock_bounds";
        }
        if(hakuna && enemy){
            if(word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
            if(pointer(actor+4)==0xc58975){choice="gameplay.levels.hakuna_matata.poison_bug_bounds";bounds_family=7;}
            else if(pointer(actor+4)==0xc58a7f){choice="gameplay.levels.hakuna_matata.gorilla_bounds";bounds_family=8;}
            else if(pointer(actor+4)==0xc586c0){choice="gameplay.levels.hakuna_matata.bonus_bug_bounds";bounds_family=4;}
            else return;
        }
        if(hunt){
            unsigned descriptor=pointer(actor+4);
            if(word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40) ||
               (descriptor!=0xc58975 && (descriptor<0xc58a11 || descriptor>0xc58a65 || (descriptor-0xc58a11)%12)))return;
            choice="gameplay.bonus.bug_hunt.bug_bounds";bounds_family=7;
        }
        if(pride && enemy && pointer(actor+4)==0xc586c0) {
            if(word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
            choice="gameplay.levels.pride_lands.bonus_bug_bounds";bounds_family=4;
        }
        if(adult && enemy) {
            if(word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
            unsigned descriptor=pointer(actor+4);
            if(descriptor==0xc58ecc)choice="gameplay.levels.adult_hyenas.bounds";
            else if(level==7&&descriptor==0xc587d6){choice="gameplay.levels.be_prepared.leaper_bounds";prepared=descriptor;}
            else if(level==7&&descriptor==0xc58780){choice="gameplay.levels.be_prepared.rock_bounds";prepared=descriptor;}
            else if(level==7&&descriptor==0xc58768){choice="gameplay.levels.be_prepared.geyser_projectile_bounds";prepared=descriptor;}
            else if(word(0x1ff9e)==9 && (descriptor==0xc585e8 || descriptor==0xc585f4 || descriptor==0xc58600)) {
                choice="gameplay.levels.pride_rock.scar_bounds";bounds_family=3;
            } else return;
        }
        if(graveyard) {
            unsigned descriptor=pointer(actor+4);
            if(word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
            if(TlkGraveyardHyenaDescriptor(descriptor)) {
                choice="gameplay.levels.elephant_graveyard.hyena_bounds";
            } else if(descriptor==0xc58cca || descriptor==0xc58cd8 || descriptor==0xc58ce6 || descriptor==0xc58cf2 || descriptor==0xc58d00) {
                choice="gameplay.levels.elephant_graveyard.vulture_bounds";bounds_family=2;
            } else if(descriptor==0xc586c0) {
                choice="gameplay.levels.elephant_graveyard.bonus_bug_bounds";bounds_family=4;
            } else return;
        }
        if(!TlkResourcesUseMd(choice))return;
        unsigned native,md;
        int contextual=adult && enemy && pointer(actor+4)==0xc58ecc &&
            TlkLateSceneHyenaBounds(pose,pointer(actor+0x12),component,&native,&md);
        if(exile){if(!TlkNextSceneExileRockBounds(pose,component,&native,&md))return;}
        else if(prepared){if(!TlkBePreparedBodyBounds(prepared,pose,component,&native,&md))return;}
        else if(!contextual&&!TlkHitboxDataGet(pose,bounds_family,component,&native,&md))return;
        unsigned before=cpu->A,input=0,result;
        if(!op) { if(before!=native)return;result=md; }
        else if(op==1) {
            input=(before-native)&65535;unsigned sum=input+md;
            result=sum&65535;cpu->_flag_C=sum>65535;
            cpu->_flag_V=!!((~(input^md)&(input^result))&32768);
        } else {
            input=(before+native)&65535;result=(input-md)&65535;
            cpu->_flag_C=input>=md;cpu->_flag_V=!!(((input^md)&(input^result))&32768);
        }
        cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int initialized;
        if(!initialized) { const char *p=getenv("TLK_HITBOX_TRACE");initialized=1;if(p)trace=fopen(p,"w");
            if(trace)fprintf(trace,"pc,actor,pose,component,native,md,before,after\n"); }
        if(trace)fprintf(trace,"%06x,%04x,%06x,%u,%04x,%04x,%04x,%04x\n",pc,actor,pose,component,native,md,before,result);
        return;
    }
}
void (*g_tlk_destiny_boulder_pc_hook)(CpuState *,uint32_t);
static void destiny_boulder_pre(CpuState *cpu,uint32_t pc){
    if(pc!=0xc0ce5c || word(0x1ff9e)!=6 || pointer(0xdf)!=0xc004b3 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_contact"))return;
    unsigned actor=word(0x68),draw,native,md,caller=word(cpu->S+4);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || pointer(actor+4)!=0xc588dd ||
       word(0x6c)!=0xb213 || g_ram[cpu->S+6]!=0xc5 || (caller!=0x94f6 && caller!=0x956f) ||
       word(cpu->S+11)!=65532 || word(cpu->S+15)!=48 || word(cpu->S+17)!=47 ||
       !TlkNextSceneDestinyBoulderTop(&native,&md) || cpu->A!=native || word(cpu->S+13)!=native)return;
    draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || (g_ram[draw+8]&128) || (g_ram[draw+9]&64))return;
    /* Original MD1AB6C0/1AB736 pass top+8 where SNES passes-2. Select
     * the real shared-helper argument load; its ordinary arithmetic,
     * contact result and original boulder pushing own everything afterward. */
    cpu->A=(uint16_t)md;cpu->_flag_N=!!(md&32768);cpu->_flag_Z=!md;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_DESTINY_BOULDER_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,caller,native,md,x,y,player_x,player_y\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%04x,%04x,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,caller,native,md,word(actor+8),word(actor+10),word(0xb21b),word(0xb21d));fflush(trace);}
}
static void destiny_boulder_after(CpuState *cpu,uint32_t pc){destiny_boulder_pre(cpu,pc+2);}
/* C0CD6F reads the target sprite directly rather than the cached player box.
 * Cover this existing body-bounds choice for adult rectangle contacts as well. */
void (*g_tlk_adult_direct_body_pc_hook)(CpuState *,uint32_t);
static const struct { unsigned load,after,component,operation,current; } direct_body_sites[]={
    {0xc0cda1,0xc0cda3,0,0},{0xc0cdb1,0xc0cdb3,2,1},
    {0xc0cdc0,0xc0cdc2,0,2},{0xc0cdcd,0xc0cdcf,2,2},
    {0xc0ce1d,0xc0ce1f,1,0},{0xc0ce2d,0xc0ce2f,3,1},
    {0xc0ce3c,0xc0ce3e,1,2},{0xc0ce49,0xc0ce4b,3,2},
    /* C0CE9B pair query reads the target body from0D, draw from0A. */
    {0xc0cf10,0xc0cf12,0,0},{0xc0cf20,0xc0cf22,2,1},
    {0xc0cf2f,0xc0cf31,0,2},{0xc0cf3c,0xc0cf3e,2,2},
    {0xc0cf9b,0xc0cf9d,1,0},{0xc0cfab,0xc0cfad,3,1},
    {0xc0cfba,0xc0cfbc,1,2},{0xc0cfc7,0xc0cfc9,3,2},
    /* Current Simba body in the same paired query; target retains its owner. */
    {0xc0ced3,0xc0ced5,0,0,1},{0xc0cee3,0xc0cee5,2,1,1},
    {0xc0cef2,0xc0cef4,0,2,1},{0xc0ceff,0xc0cf01,2,2,1},
    {0xc0cf5e,0xc0cf60,1,0,1},{0xc0cf6e,0xc0cf70,3,1,1},
    {0xc0cf7d,0xc0cf7f,1,2,1},{0xc0cf8a,0xc0cf8c,3,2,1}
};
static void adult_direct_body_pre(CpuState *cpu,uint32_t pc){
    unsigned level=word(0x1ff9e);
    int graveyard=level==2 && pointer(0xdf)==0xc003eb && !word(0x2000);
    if((!graveyard && (level<6 || level>9 || pointer(0xdf)!=0xc004b3+(level-6)*50 || word(0x2000)!=0xffff)) ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    unsigned site;
    for(site=0;site<sizeof direct_body_sites/sizeof*direct_body_sites;site++)if(pc==direct_body_sites[site].after)break;
    if(site==sizeof direct_body_sites/sizeof*direct_body_sites)return;
    unsigned current=direct_body_sites[site].current;
    int pair=pc>=0xc0cf00 && pc<=0xc0cfc9;
    unsigned actor=word(current?0x68:0x6c),draw=word(current?0x7c:pair?0x0a:0x93),pose=pointer(current?0x99:pair?0x0d:0x99);
    unsigned family=0,prepared=0,descriptor=pointer(actor+4);
    if(graveyard){
        /* Marker102's real C47F4B query reads Simba directly. Its MD body
         * operands must follow the existing body choice, independent of homes.
         * Preserve the original inclusive helper and normal spawning/RNG. */
        unsigned owner=word(0x68);
        if(current || pair || actor!=0xb213 || owner<0xb293 || owner>=0xdc13 || ((owner-0xb213)&127) ||
           pointer(owner+4)!=0xc58838 || pointer(owner+48))return;
        /* This native marker is deliberately invisible (draw pointer0),
         * unlike MD's placeholder drawing. Only Simba owns the body read. */
    }
    if(actor==0xb213){if(descriptor!=0xc5858a)return;}
    else{
        if(current||actor<0xb293||actor>=0xdc13||((actor-0xb213)&127))return;
        if(descriptor==0xc58ecc)family=1;
        else if(level==7&&(descriptor==0xc587d6||descriptor==0xc58780||descriptor==0xc58768))prepared=descriptor;
        else if(level==9&&(descriptor==0xc585e8||descriptor==0xc585f4||descriptor==0xc58600))family=3;
        else return;
    }
    const char*choice=prepared?(descriptor==0xc587d6?"gameplay.levels.be_prepared.leaper_bounds":descriptor==0xc58780?"gameplay.levels.be_prepared.rock_bounds":"gameplay.levels.be_prepared.geyser_projectile_bounds"):family==3?"gameplay.levels.pride_rock.scar_bounds":family==1?"gameplay.levels.adult_hyenas.bounds":"gameplay.hitboxes.simba";
    if(!TlkResourcesUseMd(choice))return;
    if(draw<0x8000 || draw>0xffe8 ||
       word(actor+12)!=draw || word(draw+4)!=actor+8 || pointer(draw+10)!=pose || (g_ram[draw+9]&0x40))return;
    for(unsigned i=0;i<sizeof direct_body_sites/sizeof *direct_body_sites;i++){
        if(pc!=direct_body_sites[i].after)continue;
        unsigned component=direct_body_sites[i].component,op=direct_body_sites[i].operation,native,md;
        if(cpu->Y!=12+component*2)return;
        int contextual=family==1&&TlkLateSceneHyenaBounds(pose,pointer(actor+0x12),component,&native,&md);
        if(prepared){if(!TlkBePreparedBodyBounds(prepared,pose,component,&native,&md))return;}
        else if(!contextual&&!TlkHitboxDataGet(pose,family,component,&native,&md))return;
        unsigned before=cpu->A,result;
        if(!op){if(before!=native)return;result=md;}
        else if(op==1){unsigned input=(before-native)&65535,sum=input+md;result=sum&65535;
            cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^md)&(input^result))&32768);}
        else {unsigned input=(before+native)&65535;result=(input-md)&65535;
            cpu->_flag_C=input>=md;cpu->_flag_V=!!(((input^md)&(input^result))&32768);}
        cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int opened;
        if(!opened){opened=1;const char *p=getenv("TLK_ADULT_DIRECT_BODY_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,pc,pose,component,native,md,before,after\n",trace);}}
        if(trace){fprintf(trace,"%u,%06x,%06x,%u,%04x,%04x,%04x,%04x\n",snes_frame_counter+1,pc,pose,component,native,md,before,result);fflush(trace);}return;
    }
}
static void adult_direct_body_after(CpuState *cpu,uint32_t pc){adult_direct_body_pre(cpu,pc+2);}
void TlkHitboxesInstall(void) {
    g_tlk_adult_direct_body_pc_hook=adult_direct_body_after;
    for(unsigned i=0;i<sizeof direct_body_sites/sizeof *direct_body_sites;i++)interp_bridge_add_pre_opcode_hook(direct_body_sites[i].after,adult_direct_body_pre);

    g_tlk_destiny_boulder_pc_hook=destiny_boulder_after;
    interp_bridge_add_pre_opcode_hook(0xc0ce5c,destiny_boulder_pre);
    g_tlk_cw_rhino_pc_hook=rhino_after;
    interp_bridge_add_pre_opcode_hook(0xc2e856,rhino_contact);
    for(unsigned i=0;i<sizeof sites/sizeof sites[0];i++)interp_bridge_add_pre_opcode_hook(0xc00000|sites[i].pc,pre);
    interp_bridge_add_pre_opcode_hook(0xc2ebce,TlkTailContactPostOpcode);
}
RecompReturn TlkBodyBoundsDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc0d512,3); }
RecompReturn TlkPlayerBoundsDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc0b3cc,3); }

/* Shared sprite-point helper, after original add/subtract and before its store.
 * Scene/owner guards keep monkey and cub selections independent. */
void TlkAdultPointsPostOpcode(CpuState *cpu,uint32_t pc){
    unsigned level=word(0x1ff9e),axis=pc==0xc0cb82;
    if((pc!=0xc0cb46 && pc!=0xc0cb54 && pc!=0xc0cb82) || level<6 || level>9 ||
       pointer(0xdf)!=0xc004b3+(level-6)*50 || word(0x2000)!=0xffff || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !TlkResourcesUseMd("gameplay.hitboxes.adult_points"))return;
    unsigned actor=word(0x1f),draw=word(0x93),pose=pointer(0x99),native,external;
    if(actor!=0xb213 || pointer(actor+4)!=0xc5858a || draw<0x8000 || draw>0xffe8 ||
       word(actor+12)!=draw || word(draw+4)!=actor+8 || pointer(draw+10)!=pose ||
       (g_ram[draw+9]&0x40) || cpu->Y!=20+axis*2 ||
       !TlkNextSceneSimbaPoint(pose,axis,&native,&external))return;
    unsigned before=cpu->A,result;
    if(pc==0xc0cb54){
        unsigned input=(before+native)&65535;result=(input-external)&65535;
        cpu->_flag_C=input>=external;cpu->_flag_V=!!(((input^external)&(input^result))&32768);
    }else{
        unsigned input=(before-native)&65535,sum=input+external;result=sum&65535;
        cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
    }
    cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_ADULT_POINT_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,pose,axis,native,md,before,after\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%06x,%u,%04x,%04x,%04x,%04x\n",snes_frame_counter+1,pc,pose,axis,native,external,before,result);fflush(trace);}
}
