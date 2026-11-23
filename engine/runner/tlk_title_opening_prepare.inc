/* Installer-only original title planes and fourteen Simba growth/roar poses.
 * Table28F3CE is in reverse order. The custom title draw engine submits at
 * duration+1 intervals; its first submitted pose has one construction field. */
static int prepare_title_opening(const uint8_t *rom,size_t size,uint8_t **record,size_t *bytes){
 *record=NULL;*bytes=0;uint8_t *tiles=malloc(65536),*maps=malloc(8192),*bank=calloc(1,0x8000),*data=NULL;FinalImage frames[15]={{0}};size_t tile_size=0,written=0,total=168+320*224;int ok=0;
 if(!tiles||!maps||!bank)goto done;
 if(!TlkMdDecompress(rom,size,0x295864,tiles,65536,&tile_size)||tile_size!=29920||!TlkMdDecompress(rom,size,0x299414,maps,4096,&written)||written!=4096||!TlkMdDecompress(rom,size,0x2990ea,maps+4096,4096,&written)||written!=4096||!TlkMdDecompress(rom,size,0x29e4fa,bank,0x8000,&written)||written!=6272)goto done;
 for(unsigned i=0;i<14;i++){uint32_t at=0x28f43e - i*8,frame=be32(rom+at);if(!decode_frame(frames+i,rom,size,bank,frame))goto done;total+=24+(size_t)frames[i].w*frames[i].h;}
 if(!decode_frame(frames+14,rom,size,bank,0x290c62))goto done;total+=24+(size_t)frames[14].w*frames[14].h;
 data=calloc(1,total);if(!data)goto done;memcpy(data,"TLKTIO01",8);put32(data+8,2);put32(data+12,(uint32_t)total);put32(data+16,320);put32(data+20,224);put32(data+24,14);put32(data+28,2);put32(data+160,320*224);
 for(unsigned i=0;i<64;i++){unsigned c=TlkMdColor555(be16(rom+0x2999ee + i*2));data[32+i*2]=c;data[33+i*2]=c>>8;}
 uint8_t *canvas=data+168;
 if(!ready_title_plane(canvas,maps,tiles,tile_size,0)||!ready_title_plane(canvas,maps+4096,tiles,tile_size,0)||!ready_title_plane(canvas,maps,tiles,tile_size,1)||!ready_title_plane(canvas,maps+4096,tiles,tile_size,1))goto done;
 uint8_t *p=canvas+320*224;
 for(unsigned i=0;i<15;i++){const FinalImage *f=frames+i;unsigned ticks=i==14?1:be32(rom+0x28f442-i*8)+1+(i==0);put32(p,f->frame);put32(p+4,ticks);put32(p+8,f->x);put32(p+12,f->y);put32(p+16,f->w);put32(p+20,f->h);p+=24;size_t n=(size_t)f->w*f->h;memcpy(p,f->pixels,n);p+=n;}
 *record=data;*bytes=total;data=NULL;ok=1;
done:for(unsigned i=0;i<15;i++)free(frames[i].pixels);free(data);free(tiles);free(maps);free(bank);return ok;
}
