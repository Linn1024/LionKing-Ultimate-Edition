#pragma once
/* Window size is independent of the game canvas and widescreen rules. */
static int TlkParseResolution(const char *text,int *width,int *height) {
    int w=0,h=0,n=0;char separator=0;
    if(sscanf(text," %d %c %d %n",&w,&separator,&h,&n)!=3||(separator!='x'&&separator!='X')||!n||text[n]||
       w<320||w>7680||h<224||h>4320)return 0;
    *width=w;*height=h;return 1;
}
