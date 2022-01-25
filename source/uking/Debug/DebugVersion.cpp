#include "uking/Debug/DebugVersion.hpp"

namespace ksys::skyline {

const char* GetDebuggerBuildVersion(){
#ifdef SKYLINE_DEBUG_BUILD
    return SKYLINE_DEBUG_BUILD;
#else
    return "Unknown Build";
#endif
}

}
