#include "platform.h"

#if OS_WINDOWS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <stdio.h>
#include <string.h>

void Platform_SocketsInit(void) {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
}

void Platform_SocketsCleanup(void) {
    WSACleanup();
}

void Platform_SleepMS(uint32 MS) {
    Sleep(MS);
}

int64 Platform_GetMonotonicMS(void) {
    LARGE_INTEGER Counter, Frequency;
    QueryPerformanceCounter(&Counter);
    QueryPerformanceFrequency(&Frequency);
    return (int64)((Counter.QuadPart * 1000) / Frequency.QuadPart);
}

int64 Platform_GetWallClockMS(void) {
    FILETIME FileTime;
    GetSystemTimeAsFileTime(&FileTime);
    ULARGE_INTEGER LargeInt;
    LargeInt.LowPart = FileTime.dwLowDateTime;
    LargeInt.HighPart = FileTime.dwHighDateTime;
    // Windows file time is 100ns intervals since 1601-01-01.
    // Convert to milliseconds and adjust to Unix epoch if needed?
    // For now just consistent MS is probably fine as a skeleton.
    return (int64)(LargeInt.QuadPart / 10000);
}

bool Platform_FileExists(const char* Path) {
    DWORD dwAttrib = GetFileAttributesA(Path);
    return (dwAttrib != INVALID_FILE_ATTRIBUTES && !(dwAttrib & FILE_ATTRIBUTE_DIRECTORY));
}

void Platform_PathJoin(char* Dest, usize DestSize, const char* P1, const char* P2) {
    if (P1 == NULL || P1[0] == '\0') {
        snprintf(Dest, DestSize, "%s", P2);
        return;
    }

    usize Len1 = strlen(P1);
    if (P1[Len1 - 1] == '\\' || P1[Len1 - 1] == '/') {
        snprintf(Dest, DestSize, "%s%s", P1, P2);
    } else {
        snprintf(Dest, DestSize, "%s\\%s", P1, P2);
    }
}
#endif
