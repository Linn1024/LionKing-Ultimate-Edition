/* Presentation-only palette overrides. Original CGRAM, actors and ROM data stay intact. */
enum { TLK_PALETTE_EDITS=4096 };
typedef struct { int level,layer,from,to; } TlkPaletteEdit;
static TlkPaletteEdit palette_active[TLK_PALETTE_EDITS],palette_draft[TLK_PALETTE_EDITS];
static int palette_count[2],palette_preview,palette_lut_valid[2];
static uint16_t palette_lut[2][14][3][32768];
/* Sprite entries share the transactional storage, but never the layer LUT.
 * level14 denotes all levels; layer3+node identifies a semantic palette.
 * The high bit of from distinguishes the two original colour sources. */
static struct { uint32_t key; uint16_t value; } sprite_colour_hash[2][16384];
int TlkResourcesSpritePaletteNode(int node){
 const TlkResourceNode *n=TlkResourcesNode(node);if(!n)return 0;
 size_t len=strlen(n->id);
 return len>=8&&!strcmp(n->id+len-8,".palette")&&
  (!strncmp(n->id,"graphics.sprites.",17)||!strncmp(n->id,"graphics.hud.",13)||!strncmp(n->id,"graphics.titles.",16));
}
static int PaletteEntryValid(int level,int layer,int from,int to){
 if(to<0||to>32767||from<0)return 0;
 if(level>=0&&level<14&&layer>=0&&layer<3)return from<=32767;
 return level==14&&layer>=3&&from<=65535&&TlkResourcesSpritePaletteNode(layer-3);
}
int TlkResourcesPaletteCount(int draft_mode){return palette_count[!!draft_mode];}
int TlkResourcesPaletteEntry(int index,int draft_mode,int out[4]){
 int d=!!draft_mode;if(index<0||index>=palette_count[d]||!out)return 0;
 const TlkPaletteEdit *e=(d?palette_draft:palette_active)+index;
 out[0]=e->level;out[1]=e->layer;out[2]=e->from;out[3]=e->to;return 1;
}
int TlkResourcesPaletteSet(int level,int layer,int from,int to){
 if(!PaletteEntryValid(level,layer,from,to))return 0;
 int i=0;for(;i<palette_count[1];i++){TlkPaletteEdit *e=palette_draft+i;if(e->level==level&&e->layer==layer&&e->from==from)break;}
 if((from&32767)==to){if(i<palette_count[1]){memmove(palette_draft+i,palette_draft+i+1,(palette_count[1]-i-1)*sizeof *palette_draft);palette_count[1]--;}}
 else {if(i==TLK_PALETTE_EDITS)return 0;palette_draft[i]=(TlkPaletteEdit){level,layer,from,to};if(i==palette_count[1])palette_count[1]++;}
 palette_lut_valid[1]=0;return 1;
}
void TlkResourcesPaletteReset(int level,int layer){
 for(int i=palette_count[1]-1;i>=0;i--)if((level<0||palette_draft[i].level==level)&&(layer<0||palette_draft[i].layer==layer))
  TlkResourcesPaletteSet(palette_draft[i].level,palette_draft[i].layer,palette_draft[i].from,palette_draft[i].from&32767);
}
void TlkResourcesPalettePreview(int on){palette_preview=!!on;}
static void PaletteTables(int d){
 if(!palette_lut_valid[d]){
  memset(palette_lut[d],0,sizeof palette_lut[d]);const TlkPaletteEdit *e=d?palette_draft:palette_active;
  memset(sprite_colour_hash[d],0,sizeof sprite_colour_hash[d]);
  for(int i=0;i<palette_count[d];i++){
   if(e[i].level<14)palette_lut[d][e[i].level][e[i].layer][e[i].from]=(uint16_t)(e[i].to+1);
   else {uint32_t key=((uint32_t)(e[i].layer-2)<<16)|(unsigned)e[i].from;
    unsigned slot=(key*2654435761u)>>18;
    while(sprite_colour_hash[d][slot].key&&sprite_colour_hash[d][slot].key!=key)slot=(slot+1)&16383;
    sprite_colour_hash[d][slot].key=key;sprite_colour_hash[d][slot].value=(uint16_t)(e[i].to+1);
   }
  }
  palette_lut_valid[d]=1;
 }
}
uint16_t TlkResourcesPaletteMap(unsigned level,unsigned layer,uint16_t color){
 int d=palette_preview;color&=32767;if(level>=14||layer>=3||!palette_count[d])return color;
 PaletteTables(d);
 uint16_t value=palette_lut[d][level][layer][color];return value?(uint16_t)(value-1):color;
}
uint16_t TlkResourcesSpritePaletteMap(int node,int md,uint16_t color){
 int d=palette_preview;color&=32767;if(node<0||!palette_count[d])return color;
 PaletteTables(d);uint32_t key=((uint32_t)(node+1)<<16)|((unsigned)!!md<<15)|color;
 unsigned slot=(key*2654435761u)>>18;
 while(sprite_colour_hash[d][slot].key){if(sprite_colour_hash[d][slot].key==key)return sprite_colour_hash[d][slot].value-1;slot=(slot+1)&16383;}
 return color;
}
static int PaletteDirty(void){return palette_count[0]!=palette_count[1]||memcmp(palette_active,palette_draft,palette_count[0]*sizeof *palette_active);}
static void PaletteRevert(void){palette_count[1]=palette_count[0];memcpy(palette_draft,palette_active,palette_count[0]*sizeof *palette_active);palette_lut_valid[1]=0;}
static void PaletteCommit(void){palette_count[0]=palette_count[1];memcpy(palette_active,palette_draft,palette_count[1]*sizeof *palette_active);palette_lut_valid[0]=0;}
int TlkResourcesPaletteDecode(const char *id,const char *value,int out[4]){
 unsigned l,t,c,to;char extra;
 if(!strncmp(id,"sprite_colour.",14)){
  char name[160];if(strlen(id+14)>=sizeof name)return 0;strcpy(name,id+14);
  char *shade=strrchr(name,'.');if(!shade)return 0;*shade++=0;
  char *source=strrchr(name,'.');if(!source)return 0;*source++=0;
  int node=TlkResourcesFind(name),md=!strcmp(source,"md");
  if(!TlkResourcesSpritePaletteNode(node)||(!md&&strcmp(source,"snes"))||sscanf(shade,"%x%c",&c,&extra)!=1||c>32767||sscanf(value,"%x%c",&to,&extra)!=1||to>32767)return 0;
  out[0]=14;out[1]=node+3;out[2]=(int)c|(md<<15);out[3]=(int)to;return 1;
 }
 if(strncmp(id,"colour.",7))return -1;
 if(sscanf(id,"colour.%u.%u.%x%c",&l,&t,&c,&extra)!=3||sscanf(value,"%x%c",&to,&extra)!=1||l>=14||t>=3||c>32767||to>32767)return 0;
 out[0]=(int)l;out[1]=(int)t;out[2]=(int)c;out[3]=(int)to;return 1;
}
int TlkResourcesPaletteEncode(const int e[4],char *out,size_t size){
 if(!out||!PaletteEntryValid(e[0],e[1],e[2],e[3]))return 0;
 int n=e[0]==14?snprintf(out,size,"sprite_colour.%s.%s.%04x = %04x\n",TlkResourcesNode(e[1]-3)->id,e[2]&32768?"md":"snes",e[2]&32767,e[3]):snprintf(out,size,"colour.%d.%d.%04x = %04x\n",e[0],e[1],e[2],e[3]);
 return n>=0&&(size_t)n<size;
}
static int PaletteParse(const char *id,const char *value){
 int e[4],result=TlkResourcesPaletteDecode(id,value,e);return result==1?TlkResourcesPaletteSet(e[0],e[1],e[2],e[3]):result;
}
static int PaletteWrite(FILE *f){
 for(int i=0;i<palette_count[1];i++){int e[4];char line[256];TlkResourcesPaletteEntry(i,1,e);if(!TlkResourcesPaletteEncode(e,line,sizeof line)||fputs(line,f)==EOF)return 0;}return 1;
}
