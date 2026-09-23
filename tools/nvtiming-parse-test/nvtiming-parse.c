// nvtiming-parse: run NVIDIA's EDID timing library (src/common/modeset/timing
// in open-gpu-kernel-modules) in userspace and print every timing it derives
// from an EDID file. Lets a parser change be checked against a real sink's
// EDID without loading a kernel module.
//
// S=/path/to/open-gpu-kernel-modules
// gcc -O0 -w -I$S/src/common/modeset/timing -I$S/src/common/inc \
//     -I$S/src/common/sdk/nvidia/inc -I$S/src/common/shared/inc \
//     -o nvtiming-parse nvtiming-parse.c $S/src/common/modeset/timing/*.c
// ./nvtiming-parse ../../docs/research/liverecon/hx855-edid.bin
//
// Do not define NVT_USE_NVKMS: the library then uses libc snprintf.
// SPDX-License-Identifier: CC0-1.0

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "nvtiming.h"
int main(int argc, char **argv)
{
    static unsigned char edid[512];
    FILE *f = fopen(argv[1], "rb"); size_t n = fread(edid, 1, sizeof edid, f); fclose(f);
    NVT_EDID_INFO *info = calloc(1, sizeof *info);
    NVT_STATUS st = NvTiming_ParseEDIDInfo(edid, (NvU32)n, info);
    printf("parse status %d, %u timings\n", (int)st, info->total_timings);
    for (NvU32 i = 0; i < info->total_timings; i++) {
        NVT_TIMING *t = &info->timing[i];
        printf("%-40s %4ux%-4u %c rrx1k=%6u pclk1khz=%7u type=%u vic=%u\n", (char *)t->etc.name,
               t->HVisible, t->VVisible * (t->interlaced ? 2 : 1), t->interlaced ? 'i' : 'p',
               t->etc.rrx1k, t->pclk1khz, NVT_GET_TIMING_STATUS_TYPE(t->etc.status),
               NVT_GET_CEA_FORMAT(t->etc.status));
    }
    return 0;
}
