// A stand-in tier0.dll for loading the Windows sourcevr.dll under Wine,
// outside the game: the six symbols the module imports (CommandLine_Tier0,
// Plat_FloatTime, Plat_IsInDebugSession, Warning, WriteMiniDump,
// g_pMemAlloc), with the same names and interfaces as Valve's tier0.dll.
// The allocator is the C runtime's; the command line is SVRTV_CMDLINE.
// Only for test_geometry.cpp: it proves the module loads, starts and does
// its stereo math as a Windows DLL, not that it runs inside the game.
#define TIER0_DLL_EXPORT
#include "tier0/platform.h"
#include "tier0/memalloc.h"
#include "tier0/icommandline.h"
#include "tier0/dbg.h"
#include "tier0/minidump.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <windows.h>

class CStubMemAlloc : public IMemAlloc
{
public:
	void *Alloc( size_t n ) { return malloc( n ); }
	void *Realloc( void *p, size_t n ) { return realloc( p, n ); }
	void Free( void *p ) { free( p ); }
	void *Expand_NoLongerSupported( void *, size_t ) { return NULL; }
	void *Alloc( size_t n, const char *, int ) { return malloc( n ); }
	void *Realloc( void *p, size_t n, const char *, int ) { return realloc( p, n ); }
	void Free( void *p, const char *, int ) { free( p ); }
	void *Expand_NoLongerSupported( void *, size_t, const char *, int ) { return NULL; }
	size_t GetSize( void *p ) { return p ? _msize( p ) : 0; }
	void PushAllocDbgInfo( const char *, int ) {}
	void PopAllocDbgInfo() {}
	long CrtSetBreakAlloc( long ) { return 0; }
	int CrtSetReportMode( int, int ) { return 0; }
	int CrtIsValidHeapPointer( const void * ) { return 1; }
	int CrtIsValidPointer( const void *, unsigned int, int ) { return 1; }
	int CrtCheckMemory( void ) { return 1; }
	int CrtSetDbgFlag( int ) { return 0; }
	void CrtMemCheckpoint( _CrtMemState * ) {}
	void DumpStats() {}
	void DumpStatsFileBase( char const * ) {}
	void *CrtSetReportFile( int, void * ) { return NULL; }
	void *CrtSetReportHook( void * ) { return NULL; }
	int CrtDbgReport( int, const char *, int, const char *, const char * ) { return 0; }
	int heapchk() { return -2; /* _HEAPOK */ }
	bool IsDebugHeap() { return false; }
	void GetActualDbgInfo( const char *&f, int &l ) { f = ""; l = 0; }
	void RegisterAllocation( const char *, int, int, int, unsigned ) {}
	void RegisterDeallocation( const char *, int, int, int, unsigned ) {}
	int GetVersion() { return MEMALLOC_VERSION; }
	void CompactHeap() {}
	MemAllocFailHandler_t SetAllocFailHandler( MemAllocFailHandler_t ) { return NULL; }
	void DumpBlockStats( void * ) {}
	void SetStatsExtraInfo( const char *, const char * ) {}
	size_t MemoryAllocFailed() { return 0; }
	uint32 GetDebugInfoSize() { return 0; }
	void SaveDebugInfo( void * ) {}
	void RestoreDebugInfo( const void * ) {}
	void InitDebugInfo( void *, const char *, int ) {}
	void GlobalMemoryStatus( size_t *u, size_t *f ) { if ( u ) *u = 0; if ( f ) *f = 0; }
};
static CStubMemAlloc s_MemAlloc;
DLL_EXPORT IMemAlloc *g_pMemAlloc = &s_MemAlloc;

// Parameters are the words of SVRTV_CMDLINE (e.g. "-stereo3d").
class CStubCommandLine : public ICommandLine
{
public:
	void CreateCmdLine( const char * ) {}
	void CreateCmdLine( int, char ** ) {}
	const char *GetCmdLine( void ) const { const char *c = getenv( "SVRTV_CMDLINE" ); return c ? c : ""; }
	const char *CheckParm( const char *psz, const char **ppszValue = 0 ) const
	{
		if ( ppszValue ) *ppszValue = NULL;
		const char *c = GetCmdLine(), *p = strstr( c, psz );
		size_t n = strlen( psz );
		while ( p && ( ( p != c && p[-1] != ' ' ) || ( p[n] && p[n] != ' ' ) ) )
			p = strstr( p + 1, psz );
		return p;
	}
	void RemoveParm( const char * ) {}
	void AppendParm( const char *, const char * ) {}
	const char *ParmValue( const char *, const char *d = 0 ) const { return d; }
	int ParmValue( const char *, int d ) const { return d; }
	float ParmValue( const char *, float d ) const { return d; }
	int ParmCount() const { return 0; }
	int FindParm( const char *psz ) const { return CheckParm( psz ) ? 1 : 0; }
	const char *GetParm( int ) const { return ""; }
	void SetParm( int, char const * ) {}
	const char *ParmValueByIndex( int, const char *d = 0 ) const { return d; }
	bool HasParm( const char *psz ) const { return CheckParm( psz ) != NULL; }
	const char **GetParms() const { return NULL; }
	void CreateCmdLine1( const char *, bool ) {}
	void CreateCmdLine1( int, char **, bool ) {}
};
static CStubCommandLine s_CommandLine;
PLATFORM_INTERFACE ICommandLine *CommandLine_Tier0() { return &s_CommandLine; }

PLATFORM_INTERFACE double Plat_FloatTime()
{
	static LARGE_INTEGER f, s;
	LARGE_INTEGER n;
	if ( !f.QuadPart ) { QueryPerformanceFrequency( &f ); QueryPerformanceCounter( &s ); }
	QueryPerformanceCounter( &n );
	return (double)( n.QuadPart - s.QuadPart ) / (double)f.QuadPart;
}
PLATFORM_INTERFACE bool Plat_IsInDebugSession() { return false; }
// Defined because a header this file includes (fasttimer.h, through
// dbg.h) makes a static CClockSpeedInit in every file that includes it.
#include "tier0/fasttimer.h"
void CClockSpeedInit::Init() {}
PLATFORM_INTERFACE void WriteMiniDump( const char * ) {}
DBG_INTERFACE void Warning( const tchar *pMsg, ... )
{
	va_list a;
	va_start( a, pMsg );
	fputs( "Warning: ", stdout );
	vprintf( pMsg, a );
	va_end( a );
}
