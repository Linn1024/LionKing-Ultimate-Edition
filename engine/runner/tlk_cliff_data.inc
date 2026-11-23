/* Prepared cliff payload appended after the unchanged credits record. */
static int cliff_valid(const uint8_t *p,size_t n){
    if(n<192+PIXELS || n>LIMIT || memcmp(p,"TLKCLF01",8) || get(p,8)!=1 || get(p,12)!=n)return 0;
    unsigned count=get(p,16),n0=get(p,20),n1=get(p,24),bg=get(p,44),program=get(p,40),image=get(p,36),audio=get(p,48);
    if(!count || count>MAX_FRAMES || !n0 || n0>MAX_STEPS || !n1 || n1>MAX_STEPS ||
       get(p,28)>=n0 || get(p,32)>=n1 || bg!=192 || program!=192+PIXELS ||
       image!=program+(n0+n1)*12 || image>n || audio<image || audio>n ||
       get(p,52)!=0x17c2 || get(p,56)!=0x2bbe || get(p,60)!=0x3a08 || n-audio!=0x17c2 + 0x2bbe + 0x3a08)return 0;
    for(unsigned i=0;i<64;i++)if(word(p+64+i*2)>0x7fff)return 0;
    for(unsigned i=0;i<PIXELS;i++)if(p[bg+i]>=64)return 0;
    unsigned ends=0;
    for(unsigned i=0;i<n0+n1;i++){
        const uint8_t *s=p+program+i*12;
        if(get(s,0)>=count || !get(s,4) || get(s,4)>256 || (get(s,8)&~6u))return 0;
        if(get(s,8)&4){if(i<n0)return 0;ends++;}
    }
    if(ends!=1)return 0;
    unsigned sources[MAX_FRAMES];size_t at=image;
    for(unsigned i=0;i<count;i++){
        if(at>audio || audio-at<16)return 0;const uint8_t *f=p+at;
        unsigned w=word(f+8),h=word(f+10),bytes=get(f,12);
        if(!w || !h || w>256 || h>224 || bytes!=w*h || coord(f+4)<-256 || coord(f+4)>256 ||
           coord(f+6)<-224 || coord(f+6)>224 || bytes>audio-at-16)return 0;
        for(unsigned k=0;k<i;k++)if(sources[k]==get(f,0))return 0;sources[i]=get(f,0);
        for(unsigned k=0;k<bytes;k++)if(f[16+k]>=16)return 0;
        at+=16+bytes;
    }
    return at==audio;
}
static const uint8_t *cliff_record(void){
    if(!record || get(record,8)<3)return NULL;
    unsigned credits=get(record,60);return record+credits+get(record+credits,12);
}
int TlkInterlevelDataCliffReady(void){return cliff_record()!=NULL;}
static const uint8_t *cliff_step(const uint8_t *p,unsigned program,unsigned tick,unsigned *first){
    if(!p || program>1)return NULL;
    unsigned count=get(p,20+program*4),loop=get(p,28+program*4),base=get(p,40)+(program?get(p,20)*12:0),total=0,prefix=0;
    for(unsigned i=0;i<count;i++){if(i==loop)prefix=total;total+=get(p+base+i*12,4);}
    if(tick>=total)tick=prefix+(tick-prefix)%(total-prefix);
    for(unsigned i=0;i<count;i++){const uint8_t *s=p+base+i*12;unsigned duration=get(s,4);if(tick<duration){if(first)*first=tick==0;return s;}tick-=duration;}
    return NULL;
}
unsigned TlkInterlevelDataCliffEvents(unsigned tick){
    const uint8_t *p=cliff_record();unsigned first=0;const uint8_t *s=cliff_step(p,1,tick,&first);return s&&first?get(s,8):0;
}
unsigned TlkInterlevelDataCliffPose(unsigned program,unsigned tick){
    const uint8_t *p=cliff_record();const uint8_t *s=cliff_step(p,program,tick,NULL);if(!s)return 0;
    unsigned at=get(p,36),index=get(s,0);for(unsigned i=0;i<index;i++)at+=16+get(p+at,12);return get(p+at,0);
}
int TlkInterlevelDataRenderCliff(unsigned tick,unsigned cap,unsigned loss,unsigned width,uint32_t *pixels){
    const uint8_t *p=cliff_record();if(!p || !pixels || cap>7 || loss>8 || (width!=256 && width!=320))return 0;
    uint32_t palette[64];
    for(unsigned i=0;i<64;i++){
        unsigned c=word(p+64+i*2);uint32_t rgb=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=((c>>(j*5))&31)>>2;if(v>cap)v=cap;v=v>loss?v-loss:0;v=v*4+(v>>2);rgb|=((v<<3)|(v>>2))<<((2-j)*8);}palette[i]=rgb;
    }
    unsigned start=(320-width)/2;
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<width;x++)pixels[y*width+x]=palette[p[192+y*320+x+start]];
    for(unsigned actor=0;actor<2;actor++){
        const uint8_t *s=cliff_step(p,actor,tick,NULL);unsigned at=get(p,36),index=get(s,0);
        for(unsigned i=0;i<index;i++)at+=16+get(p+at,12);const uint8_t *f=p+at;
        int ox=208+coord(f+4)-(int)start,oy=88+coord(f+6);unsigned w=word(f+8),h=word(f+10);
        for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
            unsigned value=f[16+y*w+x];int xx=ox+(int)x,yy=oy+(int)y;
            if(value && xx>=0 && xx<(int)width && yy>=0 && yy<224)pixels[yy*width+xx]=palette[16+value];
        }
    }
    return 1;
}
