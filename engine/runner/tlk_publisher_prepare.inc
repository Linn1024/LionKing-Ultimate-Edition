/* Installer-only sources proved against original startup VDP submissions.
 * 29F6BA/291372 initialize one64x32 Plane A; Plane B/SAT/scroll are cleared. */
static int prepare_publisher(const uint8_t *rom,size_t size,uint8_t **record,size_t *bytes) {
    static const uint32_t tiles_at[]={0x29f782,0x29140e,0x29140e};
    static const uint32_t map_at[]={0x29fb98,0x2947d4,0x294b0a};
    static const uint32_t palette_at[]={0x29fc12,0x294e74,0x294e74};
    static const size_t expected_tiles[]={1568,21376,21376};
    *record=NULL;*bytes=0;uint8_t *tiles=malloc(32000),*map=malloc(4096),*data=calloc(1,PUBLISHER_BYTES);int ok=0;
    if(!tiles || !map || !data || !span(size,0x29fc12,128) || !span(size,0x294e74,128) || !span(size,0x29f744,62))goto done;
    memcpy(data,"TLKPUB01",8);put32(data+8,1);put32(data+12,PUBLISHER_BYTES);put32(data+16,3);put32(data+20,320);put32(data+24,224);put32(data+28,PUBLISHER_PREFIX_TICKS);
    for(unsigned card=0;card<3;card++)for(unsigned i=0;i<64;i++) {
        unsigned c=TlkMdColor555(be16(rom+palette_at[card]+i*2));data[32+card*128+i*2]=c;data[33+card*128+i*2]=c>>8;
    }
    for(unsigned i=0;i<31;i++) {
        unsigned c=TlkMdColor555(be16(rom+0x29f744+i*2));data[416+i*2]=c;data[417+i*2]=c>>8;
    }
    for(unsigned card=0;card<3;card++) {
        size_t tile_size=0,map_size=0;
        if(!TlkMdDecompress(rom,size,tiles_at[card],tiles,32000,&tile_size) || tile_size!=expected_tiles[card] ||
           !TlkMdDecompress(rom,size,map_at[card],map,4096,&map_size) || map_size!=4096)goto done;
        uint8_t *canvas=data+478+card*PUBLISHER_PIXELS;
        if(!ready_title_plane(canvas,map,tiles,tile_size,0) || !ready_title_plane(canvas,map,tiles,tile_size,1))goto done;
        for(unsigned i=0;i<PUBLISHER_PIXELS;i++)canvas[i]&=63;
    }
    *record=data;*bytes=PUBLISHER_BYTES;data=NULL;ok=1;
done:free(data);free(tiles);free(map);return ok;
}
