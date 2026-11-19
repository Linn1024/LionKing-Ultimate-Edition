/* Independently selected MD monkey actions use ordinary native services.
 * Cross-action continuations keep the original stack frame and return normally. */
#include "tlk_destiny_monkey.h"
#include "tlk_destiny_monkey_data.h"
#include "tlk_resources.h"
#include "tlk_audio.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdlib.h>
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static void put(unsigned p,unsigned v){g_ram[p]=v;g_ram[p+1]=v>>8;}
#define mk_byte TlkDestinyMonkeyByte
static unsigned mk_ptr(unsigned a){return word(a)|(unsigned)g_ram[a+2]<<16;}
static void mk_ptr_put(unsigned a,unsigned v){put(a,v);g_ram[a+2]=v>>16;}
static void mk_load(CpuState *c,unsigned v){
 if(c->m_flag){c->A=(c->A&0xff00)|(v&255);c->_flag_N=!!(v&128);c->_flag_Z=!(v&255);}
 else{c->A=v&65535;c->_flag_N=!!(v&32768);c->_flag_Z=!(v&65535);}cpu_mirrors_to_p(c);
}
static void mk_idle(unsigned a,unsigned timer){mk_ptr_put(a+48,0xc4d1f5);mk_ptr_put(a+14,0xc250c7);put(a+44,timer);}
static void mk_stop(unsigned a){mk_ptr_put(a+14,0xc250c7);put(a+46,2);}
static int mk_wall(unsigned a){
 unsigned draw=word(a+12),v=g_ram[a+64];
 /* Original MD18EC08 reads sprite facing (bit3), then18E9F6/18E962
  * classify that wall side. The reflected movement stream flips the draw
  * independently of actor+32. Native draw bit6 is the same facing. */
 if(word(draw+8)&64)return v==0x10||v==0xf9||v==0xed||v==0xeb||v==0x8c||v==0x8e;
 return v==0x11||v==0xfa||v==0xee||v==0xec||v==0x8d||v==0x8f;
}
static unsigned mk_kind(unsigned a){unsigned v=g_ram[a+64];if((v&15)||v<0x50)return 0;return (v>>4)-(v>=0xb0?10:4);}
static unsigned mk_anim_gravity(CpuState *c){put(c->D+0x26,1);return 0xc4d194;}
uint32_t TlkDestinyMonkeyOpcode(CpuState *c,uint32_t pc){
 unsigned a=word(0x68),act=mk_ptr(a+48),level=word(0x1ff9e);
 if(level!=6 || mk_ptr(0xdf)!=0xc004b3 || word(0x2000)!=65535 || a<0xb293 || a>=0xdc13 || ((a-0xb213)&127) || mk_ptr(a+4)!=0xc586d8 || c->DB!=0x7e)return 0;
 unsigned draw=word(a+12);
 if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=a+8)return 0;
 if(pc==0xc4cf89 && act==0xc4cec3 && word(a+46)==1)TlkAudioDestinyMonkeyShot();
 if(!TlkDestinyMonkeyDataReady() || !TlkResourcesUseMd("gameplay.levels.simbas_destiny.monkey_behavior"))return 0;
 if((pc>>16)==0xc0 || !(pc>>16)){
  if(c->D)return 0;
  /* Feed only prepared animation bytes at actual original parser load boundaries. */
  unsigned cur=mk_ptr(0x14),at=cur;int width=1,yes=1;
  switch(pc&65535){
   case 0xad50:case 0xae3b:case 0xae65:case 0xae84:case 0xaecb:break;
   case 0xad5a:at+=3;break;
   case 0xad64:case 0xaebd:at+=1;width=2;break;
   case 0xadd2:case 0xae74:at+=2;break;
   case 0xadd7:case 0xae79:width=2;break;
   case 0xaef5:at+=2;width=2;break;
   default:yes=0;
  }
  unsigned v;if(yes && mk_byte(at,&v)){if(width==2){unsigned hi;if(!mk_byte(at+1,&hi))abort();v|=hi<<8;}mk_load(c,v);}return 0;
 }
 if(pc==0xc250ca || pc==0xc25130 || pc==0xc25147){
  if(c->D || c->m_flag || !c->x_flag)return 0;
  unsigned stream=act==0xc4d1f5?0:act==0xc4cec3?1:act==0xc4d029?(word(a+46)==2?3:2):act==0xc4ce13?4:99;
  if(stream==99)return 0;
  if(pc==0xc25147)stream=5;
  mk_load(c,TlkDestinyMonkeyStream(stream)&65535);return 0;
 }
 if(pc==0xc250d1 || pc==0xc25138 || pc==0xc2514f){mk_load(c,0xc2);return 0;}
 if(c->DB!=0x7e || c->m_flag || c->x_flag || c->D<0x600 || c->D>=0x1f00)return 0;
 switch(pc){
 case 0xc4cda2:
  /* MD initializes idle in the constructor and updates it normally in this tick. */
  if(!act){mk_idle(a,TlkDestinyMonkeyParameter(TLK_MONKEY_INITIAL_WAIT));return 0xc4cdb9;}break;
 case 0xc4d229:
  mk_idle(a,TlkDestinyMonkeyParameter(act==0xc4d029?TLK_MONKEY_MOVE_WAIT:TLK_MONKEY_SHOOT_WAIT));return 0xc4d198;break;
 case 0xc4d2b9:
  return word(a+44)?0xc4d442:0xc4d16f;break;
 case 0xc4d44f:
  if(act==0xc4d1f5 && word(a+44))put(a+44,word(a+44)-1);break;
 case 0xc4cef7:
  mk_ptr_put(a+48,0xc4cec3);mk_ptr_put(a+14,0xc250c7);put(a+46,0);return 0xc4d022;break;
 case 0xc4cfe7:mk_load(c,2);return 0xc4cfea;break;
 case 0xc4cfef:
  return word(a+46)==3?0xc4d15f:0xc4d01e;break;
 case 0xc4d163:
  if(act==0xc4cec3){
   if(word(0xa68e)&1){put(c->D+12,0x512d);put(c->D+14,0xc2);return 0xc4d008;}
   else return 0xc4d134;
  }else if(act==0xc4d029){
   unsigned k=mk_kind(a),r=word(0xa68e);if(k>=1 && k<=4 && r>255-k*51){mk_stop(a);return 0xc4d198;}else if(mk_wall(a)){mk_stop(a);return 0xc4d198;}else return mk_anim_gravity(c);
  }break;
 case 0xc4d05d:
  mk_ptr_put(a+48,0xc4d029);mk_ptr_put(a+14,0xc2512d);put(a+46,0);put(c->D+0x26,0);put(c->D+0x28,0x4d49);
  /* Reuse the native movement voice call. Audio independently selects PCM17. */
  return 0xc4d266;
 case 0xc4d272:
  if(act==0xc4d029 && word(0xa68c)==c->D+0x2e && word(c->D+0x28)==0x4d49){put(c->D+0x28,0);return 0xc4d198;}break;
 case 0xc4d08d:{unsigned tile=word(a+8)>>4;put(c->D+0x24,tile!=word(a+70));put(a+70,tile);put(c->D+0x26,0);break;}
 case 0xc4d0d4:
  if(word(a+46)==3)return 0xc4d134;
  else if(word(a+46)==1 && word(c->D+0x24) && mk_kind(a)){
   if(mk_kind(a)==5){mk_stop(a);return 0xc4d198;}else return 0xc4d15f;
  }else if(word(a+46)==1 && mk_wall(a)){mk_stop(a);return 0xc4d198;}
  else return mk_anim_gravity(c);break;
 case 0xc4d198:
  if(act==0xc4d029 && word(0xa68c)==c->D+0x2e && word(c->D+0x26)==1){put(c->D+0x26,2);return 0xc4d442;}
  else if(act==0xc4d029)put(c->D+0x26,0);break;
 case 0xc4d44b:
  if(act==0xc4d029 && word(c->D+0x26)==2)return 0xc4d198;break;
 case 0xc4ce47:
  /* MD falling/dead keeps its facing; both helpers set the same defeat flag. */
  mk_ptr_put(a+48,0xc4ce13);put(a+68,0);mk_ptr_put(a+14,0xc250c7);put(a+60,0);put(a+62,0);return 0xc4ce92;
 }
 return 0;
}

static const unsigned monkey_sites[]={
 0xc4cda2,0xc4d229,0xc4d2b9,0xc4d44f,0xc4cef7,0xc4cfe7,0xc4cfef,
 0xc4d163,0xc4d05d,0xc4d08d,0xc4d0d4,0xc4d198,0xc4d44b,0xc4ce47,
 0xc4d272,0xc4cf89,0xc250ca,0xc25130,0xc25147,
 0xc0ad50,0xc0ad5a,0xc0ad64,0xc0add2,0xc0add7,0xc0ae3b,0xc0ae65,
 0xc0ae84,0xc0ae74,0xc0ae79,0xc0aebd,0xc0aecb,0xc0aef5};
int TlkDestinyMonkeyHookSite(unsigned pc){
 if(pc<0x10000)pc|=0xc00000;
 for(unsigned i=0;i<sizeof monkey_sites/sizeof *monkey_sites;i++)if(pc==monkey_sites[i])return 1;
 return 0;
}
static void monkey_pre(CpuState *c,uint32_t pc){
 unsigned target=TlkDestinyMonkeyOpcode(c,pc);
 if(target)interp_bridge_pre_opcode_redirect(target);
}
void TlkDestinyMonkeyInstall(void){
 for(unsigned i=0;i<sizeof monkey_sites/sizeof *monkey_sites;i++){
  interp_bridge_add_pre_opcode_hook(monkey_sites[i],monkey_pre);
  if((monkey_sites[i]>>16)==0xc0)interp_bridge_add_pre_opcode_hook(monkey_sites[i]&65535,monkey_pre);
 }
}
