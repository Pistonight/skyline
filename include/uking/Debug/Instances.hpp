#pragma once

#include "KingSystem/System/SystemTimers.h"
#include "KingSystem/ActorSystem/actBaseProcMgr.h"

namespace ksys::skyline::Global{
    /*Links 0x02606910 _ZN4ksys7skyline6Global21sSystemTimersInstanceE (ksys::SystemTimers::sInstance) */
    extern ksys::SystemTimers* sSystemTimersInstance;
    /*Links 0x0257A018 _ZN4ksys7skyline6Global20sBaseProcMgrInstanceE (ksys::act::BaseProcMgr::sInstance)*/
    extern ksys::act::BaseProcMgr* sBaseProcMgrInstance;
}