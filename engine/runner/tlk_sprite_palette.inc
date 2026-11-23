/* Semantic ownership survives source replacement, OAM reuse and priority. */
static uint32_t s_sprite_shades[16384];
static struct { unsigned epoch; uint16_t token; } s_piece_palette[kMaxPieces];
static uint16_t PaletteToken(const char *id) {
 int node=TlkResourcesFind(id);if(node<0)return 0;
 return (uint16_t)((node+1)|(TlkResourcesUseMd(id)?32768:0));
}
static const char *SpritePaletteId(const Piece *p) {
 if(!p)return "graphics.hud.palette";
 unsigned role=SceneNpcRole(p,(p->attr>>9)&7),desc=p->actor_descriptor;
 if(BonusScene()) {
  if(s_md_level==10&&desc==0xc5858a)return "graphics.sprites.bonus.pumbaa.palette";
  if((s_md_level==10&&desc==0xc58a71)||(s_md_level>=11&&desc==0xc5858a))return "graphics.sprites.bonus.timon.palette";
  if(role==TLK_MD_SPRITE_BONUS_PUMBAA)return "graphics.sprites.bonus.pumbaa.palette";
  if(role==TLK_MD_SPRITE_BONUS_TIMON)return "graphics.sprites.bonus.timon.palette";
  if(role==TLK_MD_SPRITE_BONUS_BUG)return "graphics.sprites.bonus.bugs.palette";
 }
 if(CubPiece(p)||role==TLK_MD_SPRITE_STAMPEDE_CUB)return rd16(s_frame.ram+0x2000)==0xffff?"graphics.sprites.simba.adult.palette":"graphics.sprites.simba.cub.palette";
 if(CheckpointPiece(p)||AdultCheckpointPiece(p))return "graphics.sprites.checkpoints.palette";
 if(ContinueTokenPiece(p))return "graphics.sprites.pickups.continue_token.palette";
 if(PickupPopupPiece(p))return "graphics.sprites.effects.pickup_arrival.palette";
 if(TitlePiece(p))return "graphics.titles.pride_lands.palette";
 if(OpeningCaptionSlot(p))return "graphics.titles.remaining.palette";
 if(HudMeter(p)>=0||SharedGuidancePiece(p,p->attr))return "graphics.hud.palette";
 if(desc==0xc58814||desc==0xc5881d)return "graphics.sprites.animals.flying_creatures.palette";
 if(s_md_level==3&&(desc==0xc58b0c||desc==0xc58b18||desc==0xc58b24||desc==0xc58b30))return "graphics.sprites.stampede.wildebeests.palette";
 if(s_md_level==2&&TlkGraveyardHyenaDrawDescriptor(desc))return "graphics.sprites.enemies.hyenas.palette";
 if(s_md_level>=7&&s_md_level<=9&&desc==0xc58ecc)return "graphics.sprites.enemies.hyenas.adult.palette";
 if(s_md_level==5&&desc==0xc58a7f)return "graphics.sprites.enemies.gorilla.palette";
 if(s_md_level==9&&(desc==0xc585e8||desc==0xc585f4||desc==0xc58600))return "graphics.sprites.enemies.scar.palette";
 if(s_md_level==1){
  if(desc==0xc58c14)return "graphics.sprites.animals.rhinos.palette";
  if(desc==0xc58d60||desc==0xc58d70||desc==0xc58d80)return "graphics.sprites.animals.giraffes.palette";
  if(desc==0xc58ac7)return "graphics.sprites.animals.hippos.palette";
  for(unsigned i=0;i<sizeof cw_monkey_descriptors/sizeof *cw_monkey_descriptors;i++)if(desc==cw_monkey_descriptors[i])return "graphics.sprites.animals.monkeys.palette";
  for(unsigned i=0;i<sizeof cw_tail_descriptors/sizeof *cw_tail_descriptors;i++)if(desc==cw_tail_descriptors[i]&&((p->attr>>9)&7)==1)return "graphics.sprites.animals.rhinos.tail.palette";
  for(unsigned i=0;i<sizeof cw_ostrich_descriptors/sizeof *cw_ostrich_descriptors;i++)if(desc==cw_ostrich_descriptors[i])return "graphics.sprites.animals.ostriches.palette";
 }
 if(DestinySkyFacePiece(p))return "graphics.sprites.mufasa.palette";
 if(s_md_level==2&&!p->fixed){
  if(desc==0xc5882c)for(unsigned i=0;i<sizeof graveyard_mufasa_poses/sizeof *graveyard_mufasa_poses;i++)if(p->pose==graveyard_mufasa_poses[i])return "graphics.sprites.mufasa.palette";
  if(GraveyardSharedJaw(p)||GraveyardPillarPiece(p))return "graphics.sprites.bones.palette";
  for(unsigned i=0;i<sizeof graveyard_bone_poses/sizeof *graveyard_bone_poses;i++)if(p->pose==graveyard_bone_poses[i]&&desc==graveyard_bone_descriptors[i])return "graphics.sprites.bones.palette";
  if(p->pose==0xc30001)for(unsigned i=0;i<sizeof graveyard_falling_bone_descriptors/sizeof *graveyard_falling_bone_descriptors;i++)if(desc==graveyard_falling_bone_descriptors[i])return "graphics.sprites.bones.palette";
 }
 if(p->fixed&&!FixedEffectPiece(p))return "graphics.hud.palette";
 switch(role){
 case TLK_MD_SPRITE_HYENA:return "graphics.sprites.enemies.hyenas.palette";
 case TLK_MD_SPRITE_LIZARD:return "graphics.sprites.enemies.chameleons.palette";
 case TLK_MD_SPRITE_PORCUPINE:return "graphics.sprites.enemies.other.palette";
 case TLK_MD_SPRITE_PICKUP:return "graphics.sprites.pickups.palette";
 case TLK_MD_SPRITE_LEAVES:return "graphics.sprites.leaves.palette";
 case TLK_MD_SPRITE_DEFEAT_PUFF:return "graphics.sprites.effects.defeat_puff.palette";
 case TLK_MD_SPRITE_PICKUP_POPUP:return "graphics.sprites.effects.pickup_arrival.palette";
 case TLK_MD_SPRITE_CONTINUE_TOKEN:return "graphics.sprites.pickups.continue_token.palette";
 case TLK_MD_SPRITE_CW_RHINO:return "graphics.sprites.animals.rhinos.palette";
 case TLK_MD_SPRITE_GRAVEYARD_VULTURE:return "graphics.sprites.enemies.vultures.palette";
 case TLK_MD_SPRITE_STAMPEDE_ROCK:return "graphics.sprites.stampede.rocks.palette";
 case TLK_MD_SPRITE_GORILLA:return "graphics.sprites.enemies.gorilla.palette";
 case TLK_MD_SPRITE_LATER_ENEMY:return "graphics.sprites.enemies.other.palette";
 case TLK_MD_SPRITE_LATER_WORLD:return "graphics.sprites.world_objects.palette";
 case TLK_MD_SPRITE_LATER_EFFECT:return "graphics.sprites.world_objects.palette";
 case TLK_MD_SPRITE_LATER_PICKUP:return "graphics.sprites.pickups.palette";
 case TLK_MD_SPRITE_DESTINY_MONKEY:return "graphics.sprites.animals.monkeys.palette";
 case TLK_MD_SPRITE_ADULT_HYENA:return "graphics.sprites.enemies.hyenas.adult.palette";
 case TLK_MD_SPRITE_SCAR:return "graphics.sprites.enemies.scar.palette";
 case TLK_MD_SPRITE_BONUS_PUMBAA:return "graphics.sprites.bonus.pumbaa.palette";
 case TLK_MD_SPRITE_BONUS_TIMON:return "graphics.sprites.bonus.timon.palette";
 case TLK_MD_SPRITE_BONUS_BUG:return "graphics.sprites.bonus.bugs.palette";
 case TLK_MD_SPRITE_CW_HIPPO:return "graphics.sprites.animals.hippos.palette";
 case TLK_MD_SPRITE_COCONUT:return "graphics.sprites.enemies.gorilla.coconuts.palette";
 case TLK_MD_SPRITE_CW_RIDE_OBSTACLE:return "graphics.sprites.world_objects.ride_obstacles.palette";
 case TLK_MD_SPRITE_CW_GIRAFFE:return "graphics.sprites.animals.giraffes.palette";
 case TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT:return "graphics.sprites.bones.palette";
 case TLK_MD_SPRITE_GRAVEYARD_PILLAR:return "graphics.sprites.bones.palette";
 case kAdultCheckpointRole:return "graphics.sprites.checkpoints.palette";
 case kPorcupineArtRole:return "graphics.sprites.enemies.porcupines.palette";
 default:return "graphics.sprites.world_objects.palette";
 }
}
static uint16_t SpritePaletteToken(const Piece *p){
 if(!p)return PaletteToken("graphics.hud.palette");
 ptrdiff_t index=p-s_frame.pieces;
 if(index<0||index>=kMaxPieces)return 0;
 if(s_piece_palette[index].epoch!=s_draw_choice_epoch){
  s_piece_palette[index].epoch=s_draw_choice_epoch;s_piece_palette[index].token=PaletteToken(SpritePaletteId(p));
 }
 return s_piece_palette[index].token;
}
static unsigned SpriteCustomColor(uint16_t token,unsigned color){
 color&=32767;
 if(token){
  uint32_t key=((unsigned)(token&32767)<<16)|((unsigned)(token>>15)<<15)|color;
  unsigned slot=(key*2654435761u)>>18;
  for(unsigned n=0;n<16384;n++,slot=(slot+1)&16383)if(!s_sprite_shades[slot]||s_sprite_shades[slot]==key){s_sprite_shades[slot]=key;break;}
  unsigned mapped=TlkResourcesSpritePaletteMap((token&32767)-1,token>>15,(uint16_t)color);
  if(mapped!=color){SceneryCustomColor(4,color);return mapped;}
 }
 return SceneryCustomColor(4,color);
}
int TlkWideSpritePaletteColors(int node,int md,uint16_t *out,int capacity){
 if(!out||capacity<1||!TlkResourcesSpritePaletteNode(node))return 0;
 unsigned prefix=((unsigned)(node+1)<<16)|((unsigned)!!md<<15);int count=0;
 for(unsigned i=0;i<16384&&count<capacity;i++)if(s_sprite_shades[i]&&(s_sprite_shades[i]&0xffff8000u)==prefix)out[count++]=(uint16_t)(s_sprite_shades[i]&32767);
 /* Stable swatch positions even when rendering order changes. */
 for(int i=1;i<count;i++){uint16_t c=out[i];int j=i;while(j&&out[j-1]>c){out[j]=out[j-1];j--;}out[j]=c;}
 return count;
}
static void SpritePaletteBegin(void){memset(s_sprite_shades,0,sizeof s_sprite_shades);}
static unsigned SpriteDeathColor(unsigned level,uint16_t color){
 const char *id=level>=6?"graphics.sprites.simba.adult.palette":"graphics.sprites.simba.cub.palette";
 return SpriteCustomColor(PaletteToken(id),color);
}
