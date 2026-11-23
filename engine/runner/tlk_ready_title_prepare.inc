/* Installer-only MD ready-title recipe. Original setup29575A initializes two
 * independent64x32 planes, zero scroll and palette2999EE. Logo/copyright,
 * labels and selector are sprite objects; no screenshot data is imported. */
enum { READY_TITLE_PIXELS=320*224,READY_TITLE_BYTES=128+320*224+24*24 };
static int ready_title_plane(uint8_t *canvas,const uint8_t *map,const uint8_t *tiles,
                             size_t tile_size,unsigned priority) {
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++) {
        unsigned cell=be16(map+((y/8)*64+x/8)*2);
        if((cell>>15)!=priority)continue;
        unsigned px=x&7,py=y&7;if(cell&0x800)px=7-px;if(cell&0x1000)py=7-py;
        size_t at=(cell&2047)*32+py*4+px/2;if(at>=tile_size)return 0;
        unsigned index=(tiles[at]>>((px&1)?0:4))&15;
        if(index)canvas[y*320+x]=(uint8_t)(((cell>>9)&48)|index|(priority?64:0));
    }
    return 1;
}
static void ready_title_blit(uint8_t *canvas,const FinalImage *image,int x,int y,unsigned bank) {
    for(int py=0;py<image->h;py++)for(int px=0;px<image->w;px++) {
        int tx=x+image->x+px,ty=y+image->y+py;
        unsigned index=image->pixels[(size_t)py*image->w+px];
        if(index && tx>=0 && tx<320 && ty>=0 && ty<224)canvas[ty*320+tx]=(uint8_t)(bank*16+index);
    }
}
static int ready_title_text(const uint8_t *rom,size_t size,uint8_t *bank,uint32_t script,
                            unsigned expected_destination,unsigned expected_bytes) {
    if(!span(size,script,6))return 0;
    uint32_t destination=be32(rom+script);unsigned count=be16(rom+script+4);
    if(destination!=0xff0000u+expected_destination || !count || count>64 ||
       !span(size,script+6,count*2))return 0;
    uint32_t characters=script+6+count*2;unsigned start=expected_destination;
    /* Original text builder290FE2 copies glyphs in per-piece tile order.
     * Layout bytes contain a tile count followed by one-based character IDs. */
    for(unsigned n=0;n<count;n++) {
        unsigned entry=be16(rom+script+6+n*2)>>6;
        if((entry&3) || entry>60)return 0;
        uint32_t layout=be32(rom+0x291036+entry);
        if(!span(size,layout,1))return 0;
        unsigned tiles=rom[layout]+1,last=0;
        if(tiles>16 || !span(size,layout+1,tiles))return 0;
        for(unsigned i=0;i<tiles;i++) {
            last=rom[layout+1+i];
            if(!last || !span(size,characters,last))return 0;
            unsigned character=rom[characters+last-1];
            if(character<32 || character>127 || expected_destination<0x190 || expected_destination>0x8000-32)return 0;
            memcpy(bank+expected_destination-0x190,bank+0x400+character*32-0x190,32);
            expected_destination+=32;
        }
        characters+=last;
    }
    return expected_destination-start==expected_bytes;
}
static int ready_title_sprite(uint8_t *canvas,const uint8_t *rom,size_t size,
                              const uint8_t *bank,uint32_t frame,int x,int y,unsigned palette) {
    FinalImage image={0};if(!decode_frame(&image,rom,size,bank,frame))return 0;
    ready_title_blit(canvas,&image,x,y,palette);free(image.pixels);return 1;
}
static int prepare_ready_title(const uint8_t *rom,size_t size,uint8_t **record,size_t *bytes) {
    *record=NULL;*bytes=0;
    uint8_t *data=calloc(1,READY_TITLE_BYTES),*tiles=malloc(65536),*maps=malloc(8192),*bank=calloc(1,0x8000);
    size_t written=0,tile_size=0;int ok=0;FinalImage selector={0};
    if(!data || !tiles || !maps || !bank)goto done;
    if(!TlkMdDecompress(rom,size,0x295864,tiles,65536,&tile_size) || tile_size!=29920 ||
       !TlkMdDecompress(rom,size,0x299414,maps,4096,&written) || written!=4096 ||
       !TlkMdDecompress(rom,size,0x2990ea,maps+4096,4096,&written) || written!=4096)goto done;
    for(unsigned i=0;i<64;i++) {
        uint16_t c=TlkMdColor555(be16(rom+0x2999ee + i*2));data[i*2]=(uint8_t)c;data[i*2+1]=(uint8_t)(c>>8);
    }
    uint8_t *canvas=data+128;
    if(!ready_title_plane(canvas,maps,tiles,tile_size,0) ||
       !ready_title_plane(canvas,maps+4096,tiles,tile_size,0))goto done;
    if(!TlkMdDecompress(rom,size,0x2910de,bank+0x800-0x190,3072,&written) || written!=3072 ||
       !ready_title_text(rom,size,bank,0x28f90c,0x3200,544) ||
       !ready_title_sprite(canvas,rom,size,bank,0x28f92a,144,128,2) ||
       !ready_title_text(rom,size,bank,0x28e9b6,0x2200,4160) ||
       !ready_title_sprite(canvas,rom,size,bank,0x28ea52,32,176,2) ||
       !decode_frame(&selector,rom,size,bank,0x28fa92))goto done;
    if(selector.x!=-11 || selector.y!=-8 || selector.w!=24 || selector.h!=24)goto done;
    memcpy(data+128+READY_TITLE_PIXELS,selector.pixels,576);
    if(!ready_title_plane(canvas,maps,tiles,tile_size,1) ||
       !ready_title_plane(canvas,maps+4096,tiles,tile_size,1))goto done;
    memset(bank,0,0x8000);
    if(!TlkMdDecompress(rom,size,0x29e4fa,bank,0x8000,&written) || written!=6272 ||
       !ready_title_sprite(canvas,rom,size,bank,0x29f5ea,0,32,7) ||
       !ready_title_sprite(canvas,rom,size,bank,0x290c62,0,-16,6))goto done;
    *record=data;*bytes=READY_TITLE_BYTES;data=NULL;ok=1;
done:
    free(selector.pixels);free(data);free(tiles);free(maps);free(bank);return ok;
}
