/* Presentation-only palette overrides. Original CGRAM, actors and ROM data stay intact. */
enum { TLK_PALETTE_EDITS=1024 };
typedef struct { int level,layer,from,to; } TlkPaletteEdit;
static TlkPaletteEdit palette_active[TLK_PALETTE_EDITS],palette_draft[TLK_PALETTE_EDITS];
static int palette_count[2],palette_preview,palette_lut_valid[2];
static uint16_t palette_lut[2][14][3][32768];
int TlkResourcesPaletteCount(int draft_mode){return palette_count[!!draft_mode];}
int TlkResourcesPaletteEntry(int index,int draft_mode,int out[4]){
 int d=!!draft_mode;if(index<0||index>=palette_count[d]||!out)return 0;
 const TlkPaletteEdit *e=(d?palette_draft:palette_active)+index;
 out[0]=e->level;out[1]=e->layer;out[2]=e->from;out[3]=e->to;return 1;
}
int TlkResourcesPaletteSet(int level,int layer,int from,int to){
 if(level<0||level>=14||layer<0||layer>=3||from<0||from>32767||to<0||to>32767)return 0;
 int i=0;for(;i<palette_count[1];i++){TlkPaletteEdit *e=palette_draft+i;if(e->level==level&&e->layer==layer&&e->from==from)break;}
 if(from==to){if(i<palette_count[1]){memmove(palette_draft+i,palette_draft+i+1,(palette_count[1]-i-1)*sizeof *palette_draft);palette_count[1]--;}}
 else {if(i==TLK_PALETTE_EDITS)return 0;palette_draft[i]=(TlkPaletteEdit){level,layer,from,to};if(i==palette_count[1])palette_count[1]++;}
 palette_lut_valid[1]=0;return 1;
}
void TlkResourcesPaletteReset(int level,int layer){
 for(int i=palette_count[1]-1;i>=0;i--)if((level<0||palette_draft[i].level==level)&&(layer<0||palette_draft[i].layer==layer))
  TlkResourcesPaletteSet(palette_draft[i].level,palette_draft[i].layer,palette_draft[i].from,palette_draft[i].from);
}
void TlkResourcesPalettePreview(int on){palette_preview=!!on;}
uint16_t TlkResourcesPaletteMap(unsigned level,unsigned layer,uint16_t color){
 int d=palette_preview;color&=32767;if(level>=14||layer>=3||!palette_count[d])return color;
 if(!palette_lut_valid[d]){
  memset(palette_lut[d],0,sizeof palette_lut[d]);const TlkPaletteEdit *e=d?palette_draft:palette_active;
  for(int i=0;i<palette_count[d];i++)palette_lut[d][e[i].level][e[i].layer][e[i].from]=(uint16_t)(e[i].to+1);
  palette_lut_valid[d]=1;
 }
 uint16_t value=palette_lut[d][level][layer][color];return value?(uint16_t)(value-1):color;
}
static int PaletteDirty(void){return palette_count[0]!=palette_count[1]||memcmp(palette_active,palette_draft,palette_count[0]*sizeof *palette_active);}
static void PaletteRevert(void){palette_count[1]=palette_count[0];memcpy(palette_draft,palette_active,palette_count[0]*sizeof *palette_active);palette_lut_valid[1]=0;}
static void PaletteCommit(void){palette_count[0]=palette_count[1];memcpy(palette_active,palette_draft,palette_count[1]*sizeof *palette_active);palette_lut_valid[0]=0;}
static int PaletteParse(const char *id,const char *value){
 if(strncmp(id,"colour.",7))return -1;unsigned l,t,c,to;char extra;
 if(sscanf(id,"colour.%u.%u.%x%c",&l,&t,&c,&extra)!=3||sscanf(value,"%x%c",&to,&extra)!=1||l>=14||t>=3||c>32767||to>32767)return 0;
 return TlkResourcesPaletteSet((int)l,(int)t,(int)c,(int)to);
}
static int PaletteWrite(FILE *f){
 for(int i=0;i<palette_count[1];i++){const TlkPaletteEdit *e=palette_draft+i;if(fprintf(f,"colour.%d.%d.%04x = %04x\n",e->level,e->layer,e->from,e->to)<0)return 0;}return 1;
}
