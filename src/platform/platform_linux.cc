#include "platform.h"

#if OS_LINUX

#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdio.h>
#include <string.h>

void Platform_SocketsInit(void) {
    // No-op on Linux
}

void Platform_SocketsCleanup(void) {
    // No-op on Linux
}

void Platform_SleepMS(uint32 MS) {
    usleep(MS * 1000);
}

int64 Platform_GetMonotonicMS(void) {
    struct timespec Time;
    clock_gettime(CLOCK_MONOTONIC_COARSE, &Time);
    return ((int64)Time.tv_sec * 1000) + ((int64)Time.tv_nsec / 1000000);
}

int64 Platform_GetWallClockMS(void) {
    struct timespec Time;
    clock_gettime(CLOCK_REALTIME, &Time);
    return ((int64)Time.tv_sec * 1000) + ((int64)Time.tv_nsec / 1000000);
}

bool Platform_FileExists(const char* Path) {
    struct stat Buffer;
    return (stat(Path, &Buffer) == 0);
}

void Platform_PathJoin(char* Dest, usize DestSize, const char* P1, const char* P2) {
    if (P1 == NULL || P1[0] == '\0') {
        snprintf(Dest, DestSize, "%s", P2);
        return;
    }

    usize Len1 = strlen(P1);
    if (P1[Len1 - 1] == '/') {
        snprintf(Dest, DestSize, "%s%s", P1, P2);
    } else {
        snprintf(Dest, DestSize, "%s/%s", P1, P2);
    }
}

#endif // OS_LINUX
