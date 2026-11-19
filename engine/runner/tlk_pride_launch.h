#ifndef TLK_PRIDE_LAUNCH_H
#define TLK_PRIDE_LAUNCH_H
#include <stdio.h>
#ifdef __cplusplus
extern "C" {
#endif
void TlkPrideConfigure(const char *verified_md_path);
int TlkPrideHealthDeathSelected(void);
int TlkPrideFinalLifeSelected(void);
int TlkPrideProfileChanged(void);
char *TlkPrideSetting(const char *name);
FILE *TlkPrideFileOpen(const char *path,const char *mode);
int TlkPrideMakeDirectory(const char *path);
#ifdef __cplusplus
}
#endif
#endif
