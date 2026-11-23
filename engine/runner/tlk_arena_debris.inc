/* Source5354: exact indexed art and anchors shared by both original arena
 * particle factories. Palette remains independently selected. */
static bool SharedArenaDebris(const Piece *p,const Line *l,const uint16_t *vram,unsigned attr) {
    if(!p || p->fixed || !s_frame.stage || s_md_level!=5 || rd24(s_frame.ram+0xdf)!=0xc00481 ||
       p->size!=16 || ((attr>>9)&7)!=1 || p->local_y!=-9)return false;
    unsigned expected_hash;
    if(p->actor_descriptor==0xc58aa3 && p->pose==0xc6ff4f && p->local_x==-4)expected_hash=0xb057d9ddu;
    else if(p->actor_descriptor==0xc58aaf && p->pose==0xc6ff2e && p->local_x==-2)expected_hash=0x9aacf48du;
    else return false;
    const uint16_t *expected=TlkNextSceneNativeObj(5,1);
    if(!expected || memcmp(l->cgram+145,expected+1,15*sizeof(uint16_t)))return false;
    unsigned base=(l->obsel&7u)<<13;if(attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
    unsigned hash=2166136261u;
    for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++) {
        unsigned tile=(((((attr&255u)>>4)+(y>>3))<<4)|(((attr&15u)+(x>>3))&15));
        hash=(hash^TilePixel(vram,base+tile*16,x&7,y&7,4))*16777619u;
    }
    return hash==expected_hash;
}
