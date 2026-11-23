/* Installer only: exact native string metadata and independently decoded MD
 * images. The King title/hint are matched by text, not initial table order. */
static unsigned CaptionLe32(const uint8_t *p){return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static unsigned CaptionBe32(const uint8_t *p){return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3];}
static int CaptionCreateExtra(TlkTitleArt *art,const uint8_t *s,size_t ss,const uint8_t *m,size_t ms) {
    if(ss!=0x300000 || ms!=0x300000 || memcmp(s+0x538f3,"\xe9\x0a\x00",3) ||
       memcmp(s+0x53918,"\xa9\x25\x00",3) || memcmp(s+0x5394b,"\x69\xef\x88",3))return 0;
    for(unsigned i=0;i<CAPTION_COUNT;i++) {
        CaptionImage *c=&art->captions[i];c->level=i==14?1:i;c->hint=i==14;
        unsigned table=CaptionBe32(m+0x1d663a+c->level*4);
        unsigned expected=c->level==1?0x1d5d04:caption_frames[i];
        if(table!=expected)return 0;c->frame=caption_frames[i];
        unsigned resource=c->hint?28:29+c->level;
        unsigned at=CaptionLe32(s+0x3b90c+resource*4)&0x3fffff,x=0,y=0;
        int finished=0;
        for(unsigned n=0;n<128;n++) {
            if(at>=ss)return 0;unsigned ch=s[at++];if(!ch){finished=1;break;}
            if(ch==13){x=0;y+=16;continue;}
            if(ch==255){if(x<10)return 0;x-=10;continue;}
            if(ch!=32) {
                if((ch<65 || ch>90) && ch!=39)return 0;
                if(c->count==CAPTION_GLYPHS || x>496 || y>48)return 0;
                unsigned glyph=ch==39?37:ch-65;
                c->glyphs[c->count][0]=(uint16_t)x;c->glyphs[c->count][1]=(uint16_t)y;
                c->glyphs[c->count++][2]=(uint16_t)(0x88ef+glyph*128);
            }
            x+=16;
        }
        if(!finished || !c->count || !TlkRevivalArtDecodeMdCaption(m,ms,c->frame,c->geometry,&c->pixels))return 0;
    }
    art->caption_count=CAPTION_COUNT;return 1;
}
