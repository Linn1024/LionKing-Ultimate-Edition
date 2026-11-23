/* Installer-only translation of MD1CAD9C; no live guest snapshots as assets. */
static int prepare_cliff(const uint8_t *m,size_t mn,uint8_t **out,size_t *size){
    if(be32(m+0x1cae94)!=0x13e04c || be32(m+0x1caee0)!=0x212a26 ||
       be32(m+0x1cfdb4+4*48+16)!=0x203092 || be32(m+0x1cfdb4+4*48+20)!=0x206372 ||
       be32(m+0x1cfdb4+4*48+24)!=0x20ddfa || be32(m+0x1cfdb4+4*48+28)!=0x20e2b0 ||
       be16(m+0x1cfdb4+4*48+12)!=200 || be16(m+0x1cae7e)!=160 ||
       memcmp(m+0x1caf12,"\x08\x39\x00\x07\xff\xff\x81\x9d",8))return 0;
    uint8_t *tiles=calloc(65536,1),*maps=calloc(8192,1),*bank=malloc(32768),*layout=malloc(32768),*bg=calloc(SCREEN,1),*data=NULL;
    Image images[MAX_IMAGES]={0};Program programs[2]={0};size_t n=0,bank_size=0,total=0;unsigned count=0;int ok=0;
    if(!tiles || !maps || !bank || !layout || !bg)goto done;
    if(!TlkMdDecompress(m,mn,0x20e2b0,tiles,65536,&n) || n!=32288 ||
       !TlkMdDecompress(m,mn,0x20ddfa,maps+4096,4096,&n) || n!=3584 ||
       !TlkMdDecompress(m,mn,0x203092,layout,32768,&n) || n!=31000 ||
       !TlkMdDecompress(m,mn,0x13e04c,bank,32768,&bank_size) || bank_size!=13440)goto done;
    /* MD001442 writes two tile rows per16px map row; only40 columns/28 rows
     * are visible. Source1CAE7C begins at decoded map+160, row stride200. */
    for(unsigned y=0;y<16;y++)for(unsigned x=0;x<22;x++){
        unsigned block=be16(layout+160+y*200+x*2);
        if(block>0x20ddfa-0x206372-8)goto done;
        for(unsigned row=0;row<2;row++)memcpy(maps+(y*2+row)*128+x*4,m+0x206372+block+row*4,4);
    }
    for(unsigned i=0;i<8192;i+=2)if((be16(maps+i)&2047)>=1009)goto done;
    plane(bg,maps+4096,tiles,0);plane(bg,maps,tiles,0);plane(bg,maps+4096,tiles,1);plane(bg,maps,tiles,1);
    /* Header commands of10DD94/10DDAE install these pose streams. Phase1 in
     * the cub program is cleared by1A614C; phase2 completes the cliff scene. */
    if(be32(m+0x10dd96)!=0x10dd9e || be32(m+0x10ddb0)!=0x10ddb8 ||
       !translate_until(m,bank,bank_size,0x10dd9e,programs,images,&count,2) ||
       !translate_until(m,bank,bank_size,0x10ddb8,programs+1,images,&count,2))goto done;
    unsigned program_at=192+SCREEN,image_at=program_at+(programs[0].count+programs[1].count)*12;
    total=image_at+0x17c2 + 0x2bbe + 0x3a08;
    for(unsigned i=0;i<count;i++)total+=16+images[i].w*images[i].h;
    data=calloc(1,total);if(!data)goto done;
    memcpy(data,"TLKCLF01",8);TlkDataPut32(data+8,1);TlkDataPut32(data+12,(uint32_t)total);TlkDataPut32(data+16,count);
    for(unsigned i=0;i<2;i++){TlkDataPut32(data+20+i*4,programs[i].count);TlkDataPut32(data+28+i*4,programs[i].loop);}
    TlkDataPut32(data+36,image_at);TlkDataPut32(data+40,program_at);TlkDataPut32(data+44,192);
    TlkDataPut32(data+52,0x17c2);TlkDataPut32(data+56,0x2bbe);TlkDataPut32(data+60,0x3a08);
    for(unsigned i=0;i<64;i++)TlkDataPut16(data+64+i*2,TlkMdColor555(be16(m+0x212a26+i*2)));
    memcpy(data+192,bg,SCREEN);size_t at=program_at;
    for(unsigned i=0;i<2;i++)for(unsigned k=0;k<programs[i].count;k++){
        Step *step=programs[i].steps+k;TlkDataPut32(data+at,step->frame);TlkDataPut32(data+at+4,step->ticks);TlkDataPut32(data+at+8,step->events);at+=12;
    }
    for(unsigned i=0;i<count;i++){
        Image *f=images+i;TlkDataPut32(data+at,f->source);TlkDataPut16(data+at+4,(uint16_t)f->x);TlkDataPut16(data+at+6,(uint16_t)f->y);
        TlkDataPut16(data+at+8,f->w);TlkDataPut16(data+at+10,f->h);TlkDataPut32(data+at+12,f->w*f->h);memcpy(data+at+16,f->pixels,f->w*f->h);at+=16+f->w*f->h;
    }
    TlkDataPut32(data+48,(uint32_t)at);
    memcpy(data+at,m+0x2d4ab8,0x17c2);at+=0x17c2;memcpy(data+at,m+0x2e0000,0x2bbe);at+=0x2bbe;memcpy(data+at,m+0x2e8000,0x3a08);at+=0x3a08;
    if(at!=total)goto done;*out=data;*size=total;data=NULL;ok=1;
done:
    for(unsigned i=0;i<MAX_IMAGES;i++)free(images[i].pixels);
    free(data);free(tiles);free(maps);free(bank);free(layout);free(bg);return ok;
}
