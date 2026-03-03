#ifndef TIBIA_PLATFORM_H_
#define TIBIA_PLATFORM_H_ 1

#include "../common.hh"

void Platform_SocketsInit(void);
void Platform_SocketsCleanup(void);

void Platform_SleepMS(uint32 MS);
void Platform_SleepUS(uint64 US);

int64 Platform_GetMonotonicMS(void);
int64 Platform_GetWallClockMS(void);

bool Platform_FileExists(const char* Path);
void Platform_PathJoin(char* Dest, usize DestSize, const char* P1, const char* P2);

#endif // TIBIA_PLATFORM_H_
