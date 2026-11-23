/* Prepared publisher cards only: no ROM bytes or original program execution. */
static PublisherArt *publisher_load(const uint8_t *p,size_t size) {
    if(!p || size!=PUBLISHER_BYTES || memcmp(p,"TLKPUB01",8) ||
       get32(p+8)!=1 || get32(p+12)!=size || get32(p+16)!=3 ||
       get32(p+20)!=320 || get32(p+24)!=224 || get32(p+28)!=PUBLISHER_PREFIX_TICKS)return NULL;
    PublisherArt *art=calloc(1,sizeof *art);if(!art)return NULL;p+=32;
    for(unsigned card=0;card<3;card++)for(unsigned i=0;i<64;i++,p+=2) {
        unsigned c=p[0]|(unsigned)p[1]<<8;if(c>0x7fff){free(art);return NULL;}
        art->palette[card][i]=(uint16_t)c;
    }
    for(unsigned i=0;i<31;i++,p+=2) {
        unsigned c=p[0]|(unsigned)p[1]<<8;if(c>0x7fff){free(art);return NULL;}
        art->cycle[i]=(uint16_t)c;
    }
    for(unsigned card=0;card<3;card++)for(unsigned i=0;i<PUBLISHER_PIXELS;i++,p++) {
        if(*p>63){free(art);return NULL;}art->base[card][i]=*p;
    }
    return art;
}
unsigned TlkFinalArtPublisherPrefixTicks(const TlkFinalArt *art) {
    return art && art->publisher?PUBLISHER_PREFIX_TICKS:0;
}
int TlkFinalArtDrawPublisher(const TlkFinalArt *art,unsigned card,unsigned age,uint32_t *out) {
    if(!art || !art->publisher || card>=3 || !out)return 0;
    const PublisherArt *p=art->publisher;uint32_t colors[64];
    unsigned cycle=20-(age/3)%21;
    for(unsigned i=0;i<64;i++) {
        unsigned c=card==0 && i>=2 && i<13?p->cycle[cycle+i-2]:p->palette[card][i];
        uint32_t rgb=0xff000000u;
        for(unsigned n=0;n<3;n++){unsigned v=c>>(n*5)&31;rgb|=((v<<3)|(v>>2))<<((2-n)*8);}
        colors[i]=rgb;
    }
    for(unsigned i=0;i<PUBLISHER_PIXELS;i++)out[i]=colors[p->base[card][i]];
    return 1;
}
