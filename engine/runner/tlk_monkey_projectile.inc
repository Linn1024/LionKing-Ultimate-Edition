/* Source5344: both originals use the same indexed5x5 projectile in an8x8
 * tile. Preserve native one-pixel anchor difference; choose colors separately. */
static bool SharedMonkeyProjectile(const Piece *p,const Line *l,const uint16_t *vram,unsigned attr) {
    if(!p || p->fixed || !s_frame.stage || s_md_level!=6 || rd24(s_frame.ram+0xdf)!=0xc004b3 ||
       p->actor_descriptor!=0xc586e4 || p->pose!=0xc1e7f4 || p->size!=8 ||
       p->local_x!=-2 || p->local_y!=-4 || ((attr>>9)&7)!=0)return false;
    const uint16_t *expected=TlkNextSceneNativeObj(6,0);
    if(!expected || memcmp(l->cgram+129,expected+1,15*sizeof(uint16_t)))return false;
    unsigned base=(l->obsel&7u)<<13;if(attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
    unsigned hash=2166136261u;
    for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)
        hash=(hash^TilePixel(vram,base+(attr&255u)*16,x,y,4))*16777619u;
    return hash==0x852a65a3u;
}
