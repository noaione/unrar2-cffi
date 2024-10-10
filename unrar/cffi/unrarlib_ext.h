#include "raros.hpp"
#include "dll.hpp"
#include "version.hpp"

// same as UNRARCALLBACK but with a void * UserData to avoid tricky castings on the python side
typedef int (CALLBACK *UNRARCALLBACKPtr)(UINT msg,void * UserData,LPARAM P1,LPARAM P2);
void   PASCAL RARSetCallbackPtr(HANDLE hArcData,UNRARCALLBACKPtr Callback,void * UserData);

// Wraps RARVER_MAJOR, RARVER_MINOR, RARVER_BETA
void RARGetUnrarVersionCallback(int *major, int *minor, int *patch);

enum CONSTANTS {
    C_RAR_OM_EXTRACT = RAR_OM_EXTRACT,
    C_RAR_OM_LIST_INCSPLIT = RAR_OM_LIST_INCSPLIT,
    C_RAR_SKIP = RAR_SKIP,
    C_RAR_TEST = RAR_TEST,
    C_RAR_EXTRACT = RAR_EXTRACT,
    C_ERAR_SUCCESS = ERAR_SUCCESS,
    C_RHDF_DIRECTORY = RHDF_DIRECTORY,
    C_ERAR_BAD_PASSWORD = ERAR_BAD_PASSWORD,
    C_ERAR_MISSING_PASSWORD = ERAR_MISSING_PASSWORD
};