#ifndef TLK_CAMERA_H
#define TLK_CAMERA_H
#include "cpu_state.h"
RecompReturn TlkCameraDispatch(CpuState *cpu);
void TlkCameraInstall(void);
void TlkCameraSetWidth(int width);
int TlkCameraViewWidth(void);
int TlkCameraProfileChanged(void);
int TlkCameraActive(void);
/* Scoped validation only; clear immediately after a savestate load. */
void TlkCameraLoadViewport(int width);
#endif
