/* Native Be Prepared group behavior and ordinary update/restart control flow.
 * Source operands are installed data; game state lives in audited guest actor
 * bytes so ordinary rollback owns its lifetime. No source CPU reader. */
#include "tlk_be_prepared_behavior.h"
#include "tlk_be_prepared_data.h"
#include "tlk_resources.h"
#include "tlk_audio.h"
#include "tlk_wide.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static void put(unsigned p,unsigned v){g_ram[p]=(uint8_t)v;g_ram[p+1]=(uint8_t)(v>>8);}
static unsigned rule(unsigned i){const uint16_t*p=TlkBePreparedLeaperRules();return p?p[i]:0;}
#define LP_MAGIC 0x4c50u
#define LP_TOMB  0x4c51u
static unsigned lp_ptr(unsigned a){return word(a)|(unsigned)g_ram[a+2]<<16;}
static int lp_actor(unsigned a){return a>=0xb293 && a<0xdc13 && !((a-0xb213)&127) && lp_ptr(a+4)==0xc587d6;}
static int lp_member(unsigned a){return lp_actor(a)&&word(a+0x56)==LP_MAGIC;}
static unsigned lp_owner(void){for(unsigned a=0xb293;a<0xdc13;a+=128)if(lp_member(a)&&!word(a+0x48))return a;return 0;}
static void lp_load(CpuState *c,unsigned v){c->A=v&65535;c->_flag_N=!!(v&32768);c->_flag_Z=!(v&65535);cpu_mirrors_to_p(c);}
static void lp_link(unsigned a){
 if(lp_member(a))return;
 for(unsigned i=0x48;i<0x58;i++)if(g_ram[a+i]){fprintf(stderr,"leaper prototype occupied private field %04x+%02x\n",a,i);exit(93);}
 unsigned owner=lp_owner(),tail=0;
 if(owner){for(unsigned i=0;i<84;i++){tail=owner;unsigned n=word(owner+0x4a);if(!n)break;if(!lp_member(n))abort();owner=n;}owner=lp_owner();}
 put(a+0x48,tail);put(a+0x4a,0);put(a+0x56,LP_MAGIC);
 if(tail)put(tail+0x4a,a);
 else{put(a+0x4c,word(a+8)+rule(TLK_BP_INITIAL_X));put(a+0x4e,word(a+10)-rule(TLK_BP_INITIAL_Y));put(a+0x50,0);put(a+0x52,65535);put(a+0x54,65535);}
}
static void lp_unlink(unsigned a){
 if(!lp_member(a))return;
 unsigned prev=word(a+0x48),next=word(a+0x4a);
 if(prev&&lp_member(prev))put(prev+0x4a,next);
 if(next&&lp_member(next)){
  put(next+0x48,prev);
  if(!prev)for(unsigned i=0x4c;i<=0x54;i+=2)put(next+i,word(a+i));
 }
 put(a+0x56,LP_TOMB);
}
static void lp_tick(unsigned a){
 unsigned magic=word(a+0x56);
 if((magic!=LP_MAGIC&&magic!=LP_TOMB)||word(a+0x48))return;
 unsigned owner=lp_owner();
 if(owner){
  unsigned frame=(unsigned)snes_frame_counter+1,seen=word(owner+0x52)|word(owner+0x54)<<16;
  if(seen!=frame){
   put(owner+0x52,frame);put(owner+0x54,frame>>16);
   int timer=(int16_t)(word(owner+0x50)-1);put(owner+0x50,timer);
   if(timer<=0){put(owner+0x50,rule(TLK_BP_LEADER_PERIOD));put(owner+0x4c,word(0xb21b));put(owner+0x4e,word(0xb21d)-rule(TLK_BP_LEADER_Y_OFFSET));TlkAudioBePreparedGroupCall(owner);}
  }
 }
 if(magic==LP_TOMB)put(a+0x56,0);
}
static void lp_target(unsigned a,unsigned *x,unsigned *y){
 unsigned prev=word(a+0x48),owner=lp_owner();
 if(prev&&lp_member(prev)){*x=word(prev+8);*y=word(prev+10);}
 else if(owner){*x=word(owner+0x4c);*y=word(owner+0x4e);}
 else abort();
}
static void lp_wake(unsigned a){if(lp_member(a)&&!word(a+44))put(a+44,1);}
static void lp_log(unsigned a,uint32_t pc){
 static FILE *f;static int checked;if(!checked){checked=1;const char *p=getenv("TLK_LEAPER_PROTO_TRACE");if(p){f=fopen(p,"w");if(f)fputs("field,pc,actor,action,x,y,previous,next,owner,leader_x,leader_y,wait,state,phase\n",f);}}
 if(!f)return;unsigned owner=lp_owner();fprintf(f,"%u,%06x,%04x,%06x,%u,%u,%04x,%04x,%04x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,a,lp_ptr(a+48),word(a+8),word(a+10),word(a+0x48),word(a+0x4a),owner,owner?word(owner+0x4c):0,owner?word(owner+0x4e):0,owner?word(owner+0x50):0,word(a+44),word(a+46));fflush(f);
}
static void lp_opcode(CpuState *c,uint32_t pc){
 if(!TlkResourcesUseMd("gameplay.levels.be_prepared.leaper_behavior")||!TlkBePreparedLeaperRules()||word(0x1ff9e)!=7||lp_ptr(0xdf)!=0xc004e5||word(0x2000)!=65535||c->PB!=0xc3||c->DB!=0x7e||c->m_flag||c->x_flag||c->_flag_D||c->D<0x600||c->D>=0x1f00)return;
 unsigned a=word(0x68),act=lp_ptr(a+48);if(!lp_actor(a))return;
 if(pc==0xc38fc4&&!act){lp_link(a);lp_log(a,pc);return;}
 if(word(a+0x56)!=LP_MAGIC&&word(a+0x56)!=LP_TOMB)return;
 unsigned target=0;
 switch(pc){
 case 0xc38f06:if(act==0xc38eb4&&!word(a+44))target=0xc38f0a;break;
 case 0xc38f0a:if(act==0xc38eb4&&word(a+44))target=0xc38f9b;break;
 case 0xc38f15:if(act==0xc38eb4&&c->A==rule(TLK_BP_NATIVE_WAIT))lp_load(c,0);break;
 case 0xc38f3c:{
  lp_log(a,pc);int dx=(int16_t)(word(0xb21b)-word(a+8)),dy=(int16_t)(word(0xb21d)-word(a+10));if(dx<0)dx=-dx;if(dy<0)dy=-dy;
  /* Wide streaming may create a bat beyond the original512-pixel range.
   * Retain its real actor while it is in the selected view; otherwise the
   * one-shot spawn is consumed and the bat disappears before Simba arrives.
   * Include the original96-pixel activation lead plus32 pixels for the body;
   * a newly streamed bat may not have entered the visible picture yet.
   * Wake distances, targets and attacks below remain source-selected. */
  if((dx>rule(TLK_BP_FAR_DISTANCE)||dy>rule(TLK_BP_FAR_DISTANCE)) &&
     !TlkWideActorInView(word(a+8),word(a+10),128)){lp_unlink(a);target=0xc38d4a;}
  else if(word(a+46)){put(0xa68c,c->D+0x24);target=0xc38d74;}
  else if(word(a+44)==1){put(a+44,2);lp_wake(word(a+0x48));lp_wake(word(a+0x4a));target=0xc38f9b;}
  else if(word(a+44)){target=0xc38f06;}
  else{if(dx<=rule(TLK_BP_WAKE_X)&&dy<=rule(TLK_BP_WAKE_Y))put(a+44,1);target=0xc38f9b;}
  break;
 }
 case 0xc38dab:if(act==0xc38d65&&c->A==rule(TLK_BP_NATIVE_SPEED_FRACTION))lp_load(c,rule(TLK_BP_MD_SPEED_FRACTION));break;
 case 0xc38db0:if(act==0xc38d65&&c->A==rule(TLK_BP_NATIVE_SPEED_WHOLE))lp_load(c,rule(TLK_BP_MD_SPEED_WHOLE));break;
 case 0xc38df1:if(act==0xc38d65)target=0xc38e00;break;
 case 0xc38e22:if(act==0xc38d65){lp_log(a,pc);target=0xc38e56;}break;
 case 0xc38e70:case 0xc38e90:if(act==0xc38d65){unsigned x,y;lp_target(a,&x,&y);unsigned input=pc==0xc38e70?y:x,offset=rule(pc==0xc38e70?TLK_BP_TARGET_Y_OFFSET:TLK_BP_TARGET_X_OFFSET),result=(input-offset)&65535;c->_flag_C=input>=offset;c->_flag_V=!!(((input^offset)&(input^result))&32768);lp_load(c,result);}break;
 case 0xc38d4a:lp_unlink(a);break;
 case 0xc38f9b:case 0xc38ead:case 0xc38d5e:lp_tick(a);break;
 }
 if(target)interp_bridge_pre_opcode_redirect(target);
}
static void install_leapers(void){
 static const unsigned sites[]={0xc38fc4,0xc38f06,0xc38f0a,0xc38f15,0xc38f3c,0xc38dab,0xc38db0,0xc38df1,0xc38e22,0xc38e70,0xc38e90,0xc38d4a,0xc38f9b,0xc38ead,0xc38d5e};
 for(unsigned i=0;i<sizeof sites/sizeof *sites;i++)interp_bridge_add_pre_opcode_hook(sites[i],lp_opcode);
}

/* Native attack-animation cue phase3 returns for one entire update; MD's
 * corresponding stream sets phase1 directly and keeps animating. Preserve the
 * native sound call for now, but continue the normal update after its phase1
 * store. Randomness is consumed only by the unmodified game decision routine. */
static void lp_enemy_event(CpuState *c,uint32_t pc){
 if(!TlkResourcesUseMd("gameplay.levels.be_prepared.attack_events")||!TlkBePreparedDataReady()||word(0x1ff9e)!=7||
    lp_ptr(0xdf)!=0xc004e5||c->PB!=0xc5||c->DB!=0x7e||c->m_flag||c->x_flag||
    c->_flag_D||c->D<0x600||c->D>=0x1f00)return;
 unsigned a=word(0x68),act=lp_ptr(a+48),desc=lp_ptr(a+4);
 if(a<0xb293||a>=0xdc13||((a-0xb213)&127)||
    (desc!=0xc58ea8&&desc!=0xc58eb4&&desc!=0xc58ecc)||word(a+46)!=1)return;
 if(pc==0xc5d31c&&act==0xc5d207)interp_bridge_pre_opcode_redirect(0xc5d335);
 if(pc==0xc5d18a&&act==0xc5d069)interp_bridge_pre_opcode_redirect(0xc5d1a3);
}

/* MD HUD08FECE renders zero health; level supervisor tests death after the
 * actor round. Native HUDC00222 jumps nonlocally into restart before later
 * actors run. Finish the existing native round, then take that same nonlocal
 * restart entry. No added actor rounds, RNG calls, seeds or fabricated returns.
 * Initially restricted to the source-audited adult Be Prepared lava death. */
static int lp_lava_restart(CpuState*c){
 return TlkResourcesUseMd("gameplay.levels.be_prepared.death_update_order")&&TlkBePreparedDataReady()&&word(0x1ff9e)==7&&
  lp_ptr(0xdf)==0xc004e5&&word(0x2000)==65535&&!word(0x2004)&&
  word(0xa6ba)==65535&&lp_ptr(0xb243)==0xc3857f&&
  c->PB==0xc0&&c->DB==0x7e&&!c->D&&!c->m_flag&&!c->_flag_D;
}
static void lp_death_order_select(CpuState*c,uint32_t pc){
 if(!lp_lava_restart(c))return;
 if(pc==0xc00222&&!c->x_flag&&lp_ptr(word(0x68)+4)==0xc00001)
  interp_bridge_pre_opcode_redirect(0xc00355);
 if(pc==0xc0ac30&&c->x_flag)
  interp_bridge_pre_opcode_redirect(0xc089b7);
}

void TlkBePreparedBehaviorInstall(void){
    install_leapers();
    interp_bridge_add_pre_opcode_hook(0xc5d31c,lp_enemy_event);
    interp_bridge_add_pre_opcode_hook(0xc5d18a,lp_enemy_event);
    interp_bridge_add_pre_opcode_hook(0xc00222,lp_death_order_select);
    interp_bridge_add_pre_opcode_hook(0xc0ac30,lp_death_order_select);
}
