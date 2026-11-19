/* Read-only subject gallery used only inside the isolated preview helper.
 * Original native drawings use that level's normally loaded graphics banks;
 * Genesis drawings come from the installed reviewed image catalogue. */
#pragma once
extern "C" {
#include "tlk_md_sprites.h"
#include "tlk_next_scene_data.h"
}
#include "pride_sprite_map.h"
#include "tlk_browser_subject_poses.h"
#include "tlk_mixed_palette.h"
#include "tlk_enemy_art_family.h"
#include "tlk_browser_scene_examples.h"
#include "tlk_browser_gallery_routes.h"
extern "C" {
#include "tlk_final_art.h"
#include "tlk_interlevel_data.h"
#include "tlk_bonus_result_data.h"
#include "tlk_graveyard_data.h"
}
#include "tlk_cw_monkey_metadata.h"
#include "tlk_cw_ostrich_metadata.h"
#include "tlk_cw_tail_metadata.h"
#include "tlk_flying_creature_metadata.h"
#include "next_scene_metadata.h"
extern "C" const uint8_t *g_rom;
namespace BrowserGallery {
struct Subject { const char *prefix;unsigned level,role; };
static const Subject subjects[]={
 {"graphics.sprites.enemies.hyenas.adult",8,19},{"graphics.sprites.enemies.hyenas",0,1},
 {"graphics.sprites.enemies.scar",9,20},{"graphics.sprites.enemies.vultures",2,10},
 {"graphics.sprites.enemies.gorilla.coconuts",5,25},{"graphics.sprites.enemies.gorilla",5,13},
 {"graphics.sprites.animals.monkeys",6,18},{"graphics.sprites.animals.hippos",1,24},
 {"graphics.sprites.animals.rhinos.tail",1,105},{"graphics.sprites.animals.rhinos",1,9},{"graphics.sprites.animals.giraffes",1,27},
 {"graphics.sprites.animals.ostriches",1,102},{"graphics.sprites.animals.flying_creatures",1,103},
 {"graphics.sprites.stampede.wildebeests",3,104},
 {"graphics.sprites.world_objects.ride_obstacles",1,26},
 {"graphics.sprites.bonus.pumbaa",10,21},{"graphics.sprites.bonus.timon",10,22},
 {"graphics.sprites.bonus.bugs",10,23},{"graphics.sprites.pickups.continue_token",0,8},
 {"graphics.sprites.pickups",0,4},{"graphics.sprites.leaves",0,5},
 {"graphics.sprites.effects.defeat_puff",0,6},{"graphics.sprites.effects.pickup_arrival",0,7},
 {"graphics.sprites.bones",2,28},{"graphics.sprites.stampede.rocks",3,12},
 {"graphics.sprites.enemies.chameleons",0,2},{"graphics.sprites.enemies.porcupines",0,106},
 {"graphics.sprites.enemies.other",5,14},{"graphics.sprites.world_objects",4,15},
 {"graphics.sprites.simba.adult",6,100},{"graphics.sprites.simba.cub",0,101}
};
static const Subject *Find(const char *id) {
 for(const auto &s:subjects){size_t n=strlen(s.prefix);if(!strncmp(id,s.prefix,n)&&(!id[n]||id[n]=='.'))return &s;}
 return nullptr;
}
static int Read(unsigned at) {
 if(at>=0x7e0000&&at<0x800000)return g_ram[at-0x7e0000];
 if(at>=0xc00000&&at<0xf00000)return g_rom[at-0xc00000];return -1;
}
static int Word(unsigned at){int a=Read(at),b=Read(at+1);return a<0||b<0?-1:a|(b<<8);}
struct Bitmap {int x=10000,y=10000,w=0,h=0;std::vector<uint8_t> data;};
static bool Native(unsigned pose,Bitmap &b) {
 unsigned at=pose|0xc00000;int flags=Word(at),n=flags&127;
 if(flags<0||n<1||n>32)return false;
 int cw=Word(at+6),ch=Word(at+8);
 if(cw<1||ch<1||cw>192||ch>192)return false;
 struct Piece{int x,y,w,source,stride;};std::vector<Piece> pieces;
 if(flags&0x8000) {
  int large=flags&0x4000?(flags>>8)&63:n;if(large>n)return false;
  int a=Read(at+26),c=Read(at+27),d=Read(at+28);if(a<0||c<0||d<0)return false;
  unsigned source=a|(c<<8)|(d<<16),q=at+29;
  for(int i=0;i<large;i++,q+=4)pieces.push_back({(int16_t)Word(q),(int16_t)Word(q+2),16,(int)(source+i*64),n*64});
  if(flags&0x4000)for(int count=large*4;count<n*4&&Word(q)!=0xaaaa;count++,q+=4)
   pieces.push_back({(int16_t)Word(q),(int16_t)Word(q+2),8,(int)(source+count/4*64+(count%2)*32+(count%4/2)*n*64),32});
 } else {
  int bank=Read(at+26);if(bank<0||(bank<0xc0&&bank!=0x7e&&bank!=0x7f))return false;unsigned q=at+27;
  for(int i=0;i<64;i++,q+=6) {
   if(i>=n&&(!(flags&0x4000)||Word(q)==0xaaaa))break;
   int source=Word(q+4);if(source<0)return false;
   pieces.push_back({(int16_t)Word(q),(int16_t)Word(q+2),i<n?16:8,(bank<<16)|source,0});
  }
 }
 if(pieces.empty())return false;int right=-10000,bottom=-10000;
 for(auto p:pieces){if(abs(p.x)>192||abs(p.y)>192)return false;b.x=std::min(b.x,p.x);b.y=std::min(b.y,p.y);right=std::max(right,p.x+p.w);bottom=std::max(bottom,p.y+p.w);}
 b.w=right-b.x;b.h=bottom-b.y;if(b.w<=0||b.h<=0||b.w>256||b.h>256)return false;b.data.assign(b.w*b.h,0);
 for(auto i=pieces.rbegin();i!=pieces.rend();i++)for(int y=0;y<i->w;y++)for(int x=0;x<i->w;x++) {
  unsigned a=i->source+(i->stride?(x/8)*32+(y/8)*i->stride:((y/8)*2+x/8)*32)+(y&7)*2;unsigned v=0;
  for(int plane=0;plane<4;plane++){int value=Read(a+(plane&1)+(plane>=2?16:0));if(value<0)return false;v|=((value>>(7-(x&7)))&1)<<plane;}
  if(v)b.data[(i->y-b.y+y)*b.w+i->x-b.x+x]=(uint8_t)v;
 }
 return std::any_of(b.data.begin(),b.data.end(),[](uint8_t v){return v!=0;});
}
static uint32_t Color(unsigned c){return 0xff000000u|((c&31)*255/31)<<16|(((c>>5)&31)*255/31)<<8|((c>>10)&31)*255/31;}
/* Still portraits use the settled daylight palette, not the short sunrise
 * entry palette. This is also the original palette loaded at checkpoints. */
static bool KingDaylight(uint16_t colors[64]) {
 uint16_t words[64];if(!TlkMdCantWaitInitialPalette(1,words))return false;
 for(unsigned i=0;i<64;i++)colors[i]=TlkMdColor555(words[i]);return true;
}
static bool Shared(const char *id,const char *path,unsigned level) {
 const unsigned *poses=nullptr;unsigned size=0,bank=0,md_bank=0;
 if(!strncmp(id,"graphics.sprites.animals.ostriches",33)){poses=cw_ostrich_poses;size=sizeof cw_ostrich_poses/sizeof *poses;bank=md_bank=2;}
 else if(!strncmp(id,"graphics.sprites.animals.monkeys",31)&&level==1){poses=cw_monkey_poses;size=sizeof cw_monkey_poses/sizeof *poses;bank=md_bank=2;}
 else if(!strncmp(id,"graphics.sprites.animals.rhinos.tail",35)){poses=cw_tail_poses;size=sizeof cw_tail_poses/sizeof *poses;bank=md_bank=1;}
 else if(!strncmp(id,"graphics.sprites.animals.flying_creatures",40)){poses=flying_creature_poses;size=sizeof flying_creature_poses/sizeof *poses;}
 else if(!strncmp(id,"graphics.sprites.stampede.wildebeests",36)){poses=next_wildebeest_poses;size=sizeof next_wildebeest_poses/sizeof *poses;bank=6;md_bank=3;}
 if(!poses)return false;
 uint16_t converted[64];const uint16_t *md=TlkNextSceneMdPalette(level);
 if(level==1&&KingDaylight(converted))md=converted;
 if(!md&&!TlkMdScenePaletteColors(level,converted))return false;if(!md)md=converted;
 std::vector<uint32_t> frames;unsigned count=0;
 for(unsigned i=0;i<size&&count<12;i++) {
  Bitmap b;if(!Native(poses[i]&0x3fffff,b)||b.w>172||b.h>172)continue;
  std::vector<uint32_t> pair(4*192*192,0);
  for(int source=0;source<4;source++)for(int y=0;y<b.h;y++)for(int x=0;x<b.w;x++) {
   unsigned pixel=b.data[y*b.w+x];if(!pixel)continue;
   unsigned c=(source&1)?md[md_bank*16+pixel]:g_snes->ppu->cgram[128+bank*16+pixel];
   pair[source*192*192+((192-b.h)/2+y)*192+(192-b.w)/2+x]=Color(c);
  }
  frames.insert(frames.end(),pair.begin(),pair.end());count++;
 }
 if(!count)return false;SDL_IOStream *f=SDL_IOFromFile(path,"wb");if(!f)return false;uint32_t header[5]={0x33474c54,192,192,count,4};bool ok=SDL_WriteIO(f,header,sizeof header)==sizeof header&&SDL_WriteIO(f,frames.data(),frames.size()*4)==frames.size()*4;SDL_CloseIO(f);return ok;
}
static bool Save(const char *path,unsigned width,unsigned height,unsigned count,unsigned planes,const std::vector<uint32_t> &pixels) {
 SDL_IOStream *f=SDL_IOFromFile(path,"wb");if(!f)return false;
 uint32_t header[5]={0x33474c54,width,height,count,planes};
 bool ok=SDL_WriteIO(f,header,sizeof header)==sizeof header&&SDL_WriteIO(f,pixels.data(),pixels.size()*4)==pixels.size()*4;
 SDL_CloseIO(f);return ok;
}
static TlkFinalArt *MenuArt() {
 static TlkFinalArt *art=nullptr;static bool tried=false;if(tried)return art;tried=true;
 int argc=0;LPWSTR *args=CommandLineToArgvW(GetCommandLineW(),&argc);if(!args)return nullptr;
 for(int i=1;i+1<argc;i++)if(!wcscmp(args[i],L"--final-menu-assets")) {
  FILE*f=_wfopen(args[i+1],L"rb");if(f){std::fseek(f,0,SEEK_END);long n=std::ftell(f);std::rewind(f);
   if(n>0&&n<=64*1024*1024){std::vector<uint8_t> data(n);if(std::fread(data.data(),1,n,f)==(size_t)n)art=TlkFinalArtLoad(data.data(),data.size());}std::fclose(f);}break;
 }LocalFree(args);return art;
}
static bool WriteSpecial(const char *id,const char *path) {
 int kind=TlkBrowserSpecialGallery(id);if(!kind)return false;
 if(kind==9||kind==17) {
  unsigned draw=g_ram[0xb21f]|(unsigned)g_ram[0xb220]<<8;if(draw>0xffe8)return false;
  unsigned pose=g_ram[draw+10]|(unsigned)g_ram[draw+11]<<8|(unsigned)g_ram[draw+12]<<16;
  uint8_t brightness[224];memset(brightness,15,sizeof brightness);std::vector<uint32_t> pixels(6*4*320*224);
  for(unsigned frame=0;frame<6;frame++)for(unsigned source=0;source<(kind==17?2u:4u);source++)
   if(!TlkInterlevelDataRenderTimon(pose,frame*16,1,kind==17?0:source>>1,kind==17?0:source&1,kind==17?(source?128:160):160,kind==17?(source?32:64):112,320,g_snes->ppu->cgram+128,brightness,pixels.data()+(frame*(kind==17?2:4)+source)*320*224))return false;
  if(kind==17)pixels.resize(6*2*320*224);return Save(path,320,224,6,kind==17?2:4,pixels);
 }
 if(kind>=11&&kind<=16) {
  unsigned count=kind==13?5:kind==16?3:4;std::vector<uint32_t> pixels(count*2*320*224,0);
  auto *art=kind==16?MenuArt():nullptr;
  static const unsigned poses[]={0xc0186d,0xc018a8,0xc018e3,0xc01922,0xc0195d};
  for(unsigned frame=0;frame<count;frame++) {
   uint32_t *md=pixels.data()+(frame*2+1)*320*224;int ok=0;
   if(kind==11)ok=TlkInterlevelDataRender(frame*90,15,320,md);
   if(kind==12)ok=TlkInterlevelDataRenderCliff(frame*45,7,0,320,md);
   if(kind==13||kind==14)ok=TlkInterlevelDataRenderEnding(poses[frame%5],15,320,md);
   if(kind==14&&ok)ok=TlkInterlevelDataRenderEndingTitle(15,320,md);
   if(kind==15)ok=TlkInterlevelDataRenderCredits(672+frame*480,15,320,md);
   if(kind==16&&art)ok=TlkFinalArtDrawMenu(art,124+frame*12,frame==0?0:frame==1?1:9,0,md);
   if(!ok)return false;for(unsigned n=0;n<320*224;n++)md[n]|=0xff000000u;
  }return Save(path,320,224,count,2,pixels);
 }
 if(kind==18) {
  static const unsigned poses[]={0xc2fe4f,0xc2feaa,0xc2ff01,0xc2ff58,0xc2ffaf};
  uint16_t colors[8];if(!TlkGraveyardFarewellPalette(colors))return false;
  std::vector<uint32_t> pixels(5*2*192*192,0);
  for(unsigned frame=0;frame<5;frame++) {
   Bitmap b;if(!Native(poses[frame]&0x3fffff,b))return false;
   for(int y=0;y<b.h;y++)for(int x=0;x<b.w;x++) {
    unsigned v=b.data[y*b.w+x];int xx=x+(192-b.w)/2,yy=y+(192-b.h)/2;
    if(v>=8&&xx>=0&&xx<192&&yy>=0&&yy<192)pixels[(frame*2+1)*192*192+yy*192+xx]=Color(TlkMdColor555(colors[v-8]));
   }
  }return Save(path,192,192,5,2,pixels);
 }
 if(kind==10) {
  std::vector<uint32_t> pixels(3*2*320*224);static const unsigned counts[]={0,12,42};
  for(unsigned frame=0;frame<3;frame++)for(unsigned source=0;source<2;source++)
   if(!TlkBonusResultDataRender(counts[frame],source,7,0,320,pixels.data()+(frame*2+source)*320*224))return false;
  return Save(path,320,224,3,2,pixels);
 }
 if(kind>=4) {
  auto *art=MenuArt();if(!art)return false;std::vector<uint32_t> pixels(2*320*224);
  if(!TlkWidePreview(pixels.data(),320))return false;
  uint32_t *md=pixels.data()+320*224;int ok=0;
  if(kind==4)ok=TlkFinalArtDrawReadyTitle(art,0,120,md);
  if(kind==5){const char buttons[3]={'A','C','B'};ok=TlkFinalArtDrawOptions(art,0,43,1,1,1,buttons,md);}
  if(kind==6)ok=TlkFinalArtDrawPublisher(art,1,0,md);
  if(kind==7)ok=TlkFinalArtDrawSoundTestCatalog(art,0,0,80,md);
  if(kind==8)ok=TlkFinalArtDrawDebugMenu(art,0,26,0,0,md);
  if(!ok)return false;
  for(auto &p:pixels)p|=0xff000000u;return Save(path,320,224,1,2,pixels);
 }
 unsigned count=kind==1?3:kind==3&&!strcmp(id,"graphics.hud.palette")?3:1;
 unsigned width=kind==2?320:192,height=kind==2?224:192;
 std::vector<uint32_t> pixels(count*4*width*height,0);
 if(kind==1||kind==2) {
  static const unsigned poses[]={0xc456de,0xc2fde1,0xc2fe18};
  for(unsigned frame=0;frame<count;frame++)for(unsigned source=0;source<4;source++) {
   int x0=-80,y0=-80,w=160,h=160;
   if(kind==2&&!TlkResourcesTitleBounds(source>>1,&x0,&y0,&w,&h))return false;
   if(w>(int)width||h>(int)height)return false;
   unsigned opaque=0;
   for(int y=0;y<h;y++)for(int x=0;x<w;x++) {
    uint16_t color=0;int sample=kind==1?TlkResourcesCheckpointSample(poses[frame],x+x0,y+y0,source>>1,source&1,g_snes->ppu->cgram,&color):
        TlkResourcesTitleSample(x+x0,y+y0,source>>1,source&1,g_snes->ppu->cgram,&color);
    if(sample<0)return false;if(sample){pixels[(frame*4+source)*width*height+(y+(height-h)/2)*width+x+(width-w)/2]=Color(color);opaque++;}
   }if(!opaque)return false;
  }
 } else if(kind==3) {
  static const char *fields[]={"graphics.hud.frames.roar","graphics.hud.frames.health","graphics.hud.frames.lives"};
  for(unsigned frame=0;frame<count;frame++) {
   unsigned part=count==3?frame:strstr(id,"health")?1:strstr(id,"lives")?2:0;
   int x0=part==1?224:0,y0=part==2?180:0,w=part==2?100:96,h=44;
   for(unsigned source=0;source<4;source++) {
    TlkResourcesSet(TlkResourcesFind(fields[part]),source&2?TLK_SOURCE_MD:TLK_SOURCE_SNES);
    TlkResourcesSet(TlkResourcesFind("graphics.hud.palette"),source&1?TLK_SOURCE_MD:TLK_SOURCE_SNES);
    if(!TlkResourcesApply())return false;std::vector<uint32_t> canvas(320*224);if(!TlkWidePreview(canvas.data(),320))return false;
    for(int y=0;y<h;y++)for(int x=0;x<w;x++)pixels[(frame*4+source)*width*height+(y+(height-h)/2)*width+x+(width-w)/2]=canvas[(y+y0)*320+x+x0]|0xff000000u;
   }
  }
 }
 return Save(path,width,height,count,4,pixels);
}
static bool Write(const char *id,const char *path) {
 if(WriteSpecial(id,path))return true;
 const Subject *s=Find(id);
 unsigned level=g_ram[0x1ff9e]|(unsigned)g_ram[0x1ff9f]<<8;
 if(Shared(id,path,level))return true;
 if(!s&&TlkBrowserSceneExample(id,level)==(int)level) {
  std::vector<uint32_t> image(320*224*2);int node=TlkResourcesFind(id);if(node<0)return false;
  for(int source=0;source<2;source++){TlkResourcesPreviewBegin(node,source?TLK_SOURCE_MD:TLK_SOURCE_SNES);bool ok=TlkWidePreview(image.data()+source*320*224,320);TlkResourcesPreviewEnd();if(!ok)return false;for(unsigned i=0;i<320*224;i++)image[source*320*224+i]|=0xff000000u;}
  SDL_IOStream *f=SDL_IOFromFile(path,"wb");if(!f)return false;uint32_t header[5]={0x33474c54,320,224,1,2};bool ok=SDL_WriteIO(f,header,sizeof header)==sizeof header&&SDL_WriteIO(f,image.data(),image.size()*4)==image.size()*4;SDL_CloseIO(f);return ok;
 }
 if(!s)return false;
 std::vector<uint32_t> frames;unsigned count=0;
 const auto *mdpal=TlkNextSceneMdPalette(s->level);
 /* The prepared scene palette API covers later scenes; earlier palettes use
  * the same initialized scene-color API as the actual compositor. */
 uint16_t early[64];
 if(s->level==1&&KingDaylight(early))mdpal=early;
 else if(!mdpal&&TlkMdScenePaletteColors(s->level,early))mdpal=early;
 for(const auto &m:sprite_map) {
  bool match=m.role==s->role;
  if(s->role==2)match=m.role==2 && !TlkEnemyArtPorcupine(m.snes);
  if(s->role==106)match=m.role==2 && TlkEnemyArtPorcupine(m.snes);
  if(s->role==23)match=m.role==4;
  if(s->role==100)match=std::binary_search(std::begin(browser_adult_poses),std::end(browser_adult_poses),m.snes);
  if(s->role==101)match=std::binary_search(std::begin(browser_cub_poses),std::end(browser_cub_poses),m.snes);
  if(s->role==1&&s->level==0)match=std::binary_search(std::begin(browser_pride_hyena_poses),std::end(browser_pride_hyena_poses),m.snes);
  if(!match)continue;Bitmap b;if(!Native(m.snes,b))continue;
  int mx,my,mw,mh;if(!TlkMdSpritesBounds(m.snes,&mx,&my,&mw,&mh))continue;
  int left=std::min(b.x,mx),top=std::min(b.y,my),right=std::max(b.x+b.w,mx+mw),bottom=std::max(b.y+b.h,my+mh);
  if(right-left>160||bottom-top>160)continue;
  std::vector<uint32_t> pair(4*192*192,0);unsigned np=m.native_palette,mp=m.md_palette;
  if(m.role==0){np=0;mp=0;}
  unsigned used=0;
  for(int y=my;y<my+mh;y++)for(int x=mx;x<mx+mw;x++) {
   int v=TlkMdSpritesPixel(m.snes,x,y);if(v>0)used|=1u<<v;
  }
  for(int source=0;source<4;source++)for(int y=top;y<bottom;y++)for(int x=left;x<right;x++) {
   int ix=x-b.x,iy=y-b.y;int v=(source&2)?TlkMdSpritesPixel(m.snes,x,y):(ix>=0&&iy>=0&&ix<b.w&&iy<b.h?b.data[iy*b.w+ix]:0);
   if(v<=0)continue;unsigned index=v;
   if(m.role && source==1) {
    index=m.native_to_md[v];
    if(mdpal)index=TlkMixedPaletteIndex(index,g_snes->ppu->cgram[128+(np&7)*16+v],mdpal+(mp&3)*16,used);
   }
   if(m.role && source==2)index=m.md_to_native[v];
   unsigned c=(source&1)&&mdpal?mdpal[(mp&3)*16+index]:g_snes->ppu->cgram[128+(np&7)*16+index];
   pair[source*192*192+(y-top+(192-(bottom-top))/2)*192+x-left+(192-(right-left))/2]=Color(c);
  }
  frames.insert(frames.end(),pair.begin(),pair.end());if(++count==12)break;
 }
 if(!count)return false;SDL_IOStream *f=SDL_IOFromFile(path,"wb");if(!f)return false;
 uint32_t header[5]={0x33474c54,192,192,count,4};bool ok=SDL_WriteIO(f,header,sizeof header)==sizeof header&&SDL_WriteIO(f,frames.data(),frames.size()*4)==frames.size()*4;SDL_CloseIO(f);
 std::fprintf(stderr,"browser_gallery id=%s frames=%u level=%u\n",id,count,s->level);return ok;
}
}
