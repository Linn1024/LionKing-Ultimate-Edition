/* Source5363: original generic effect has two shared indexed images. Keep
 * existing native anchors; original current-scene MD palette0 is independent. */
static bool SharedAmbientEffect(const Piece *p,const Line *l,const uint16_t *vram,unsigned attr) {
    if(!p || p->fixed || !s_frame.stage || s_md_level<4 || s_md_level>9 ||
       p->actor_descriptor!=0xc58e90 || p->size!=8 || ((attr>>9)&7)!=0 || p->local_x!=-1)return false;
    unsigned expected_hash;
    if(p->pose==0xc48620 && p->local_y==-3)expected_hash=0x8c59b80bu;
    else if(p->pose==0xc48643 && p->local_y==1)expected_hash=0x5a0d6493u;
    else return false;
    const uint16_t *expected=TlkNextSceneNativeObj(s_md_level,0);
    if(!expected || memcmp(l->cgram+129,expected+1,15*sizeof(uint16_t)))return false;
    unsigned base=(l->obsel&7u)<<13;if(attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
    unsigned hash=2166136261u;
    for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)
        hash=(hash^TilePixel(vram,base+(attr&255u)*16,x,y,4))*16777619u;
    return hash==expected_hash;
}
