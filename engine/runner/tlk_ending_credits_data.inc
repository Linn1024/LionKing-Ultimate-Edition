/* Prepared original credits:40 columns,260 rows,37 decoded8x8 glyphs.
 * Original1CEF0C streams map rows into a64-column VRAM ring and advances
 * vertical scroll once per3 fields. Render the bounded source directly;
 * the ring is storage, not a repeating background/content edge. */
enum { CR_HEADER=64,CR_FONT=192,CR_TILES=37,CR_ROWS=260,CR_MAP=CR_FONT+CR_TILES*64,
       CR_SIZE=CR_MAP+CR_ROWS*40*2 };
static int credits_valid(const uint8_t *p,size_t n){
    if(!p || n!=CR_SIZE || memcmp(p,"TLKCRD01",8) || get(p,8)!=1 || get(p,12)!=n ||
       get(p,16)!=CR_ROWS || get(p,20)!=CR_TILES || get(p,24)!=CR_FONT || get(p,28)!=CR_MAP)return 0;
    for(unsigned i=32;i<CR_HEADER;i++)if(p[i])return 0;
    for(unsigned i=0;i<64;i++)if(word(p+CR_HEADER+i*2)>0x7fff)return 0;
    for(unsigned i=CR_FONT;i<CR_MAP;i++)if(p[i]>=16)return 0;
    for(unsigned i=CR_MAP;i<CR_SIZE;i+=2){unsigned v=word(p+i);
        if((v&0x7ff)>=CR_TILES || (v&0xf800 && (v&0xf800)!=0x2000))return 0;}
    return 1;
}
static const uint8_t *credits_record(void){return record && get(record,8)>=2?record+get(record,60):NULL;}
int TlkInterlevelDataCreditsReady(void){return credits_record()!=NULL;}
int TlkInterlevelDataRenderCredits(unsigned tick,unsigned brightness,unsigned width,uint32_t *pixels){
    const uint8_t *p=credits_record();
    if(!p || !pixels || brightness>15 || (width!=256 && width!=320))return 0;
    uint32_t palette[64];
    for(unsigned i=0;i<64;i++){
        unsigned c=word(p+CR_HEADER+i*2);uint32_t rgb=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=((c>>(j*5))&31)>>2;v=(v*4+(v>>2))*brightness/15;
            rgb|=((v<<3)|(v>>2))<<((2-j)*8);}palette[i]=rgb;
    }
    /* Bound the arithmetic after the final blank tail; never wrap the text. */
    unsigned scroll=tick>10000?CR_ROWS*8+224:tick/3,start=(320-width)/2;
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<width;x++){
        int sy=(int)scroll+(int)y-224;unsigned value=0;
        if(sy>=0 && sy<CR_ROWS*8){unsigned sx=x+start;
            unsigned cell=word(p+CR_MAP+((sy/8)*40+sx/8)*2);
            unsigned ink=p[CR_FONT+(cell&0x7ff)*64+(sy&7)*8+(sx&7)];
            value=((cell>>13)&1)*16+ink;
        }
        pixels[y*width+x]=palette[value];
    }
    return 1;
}
