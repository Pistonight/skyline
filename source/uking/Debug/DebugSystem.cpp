#include "uking/Debug/DebugSystem.hpp"
#include "uking/Debug/DebugVersion.hpp"

#include <KingSystem/System/SystemTimers.h>
#include <KingSystem/ActorSystem/actBaseProcMgr.h>

#include <KingSymbols150.hpp>

namespace ksys::skyline{
// Debug Data
static s32 sUnloadCheckFrame;
static act::BaseProc* sLastElevator;

void Init(){
    //Calling this so the function is not removed by linker
    RenderDebugScreen(nullptr);
    ComputeDebugData();
    sUnloadCheckFrame = -1;
    sLastElevator = nullptr;
}

void ComputeDebugData(){
    ksys::SystemTimers* systemTimers = ksys::SystemTimers::instance();
    if(systemTimers){
        sUnloadCheckFrame = systemTimers->mFrameCounter % 30;
        //if(systemTimers->mFrameCounter > 1800) {
            act::BaseProcMgr* baseProcMgr = ksys::act::BaseProcMgr::instance();
            if(baseProcMgr){
                sLastElevator = baseProcMgr->getProc("DgnObj_EntranceElevator_A_01", {});
            }else{
                sLastElevator = nullptr;
            }
        //}
    }else{
        sUnloadCheckFrame = -1;
    }

}

void RenderDebugScreen(sead::TextWriter* textWriter){
    if (!textWriter) {
        // Dummy check so we could call this function in skyline so that the linker does not optimize it out
        return;
    }
    textWriter->printf("Skyline (%s)\n", GetDebuggerBuildVersion());

    
    ksys::SystemTimers* systemTimers = ksys::SystemTimers::instance();
    textWriter->printf("ksys::SystemTimers 0x%08x\n", systemTimers);
    if(systemTimers){
        textWriter->printf("    mFrameCounter     %d\n", systemTimers->mFrameCounter);
        textWriter->printf("    mFrameCounter2    %d\n", systemTimers->mFrameCounter2);
        textWriter->printf("    mvfrTimer     %f\n", systemTimers->mVfrTimer);
        textWriter->printf("    mFrameCounterB    %d\n", systemTimers->mFrameCounterB);
        textWriter->printf("    mvfrTimer2    %f\n", systemTimers->mVfrTimer2);
        textWriter->printf("    mFrameCounterB2   %d\n", systemTimers->mFrameCounterB2);
    }
    if(sUnloadCheckFrame != -1){
        textWriter->printf("sUnloadCheckFrame %02d\n", sUnloadCheckFrame);
    }
    
    
    ksys::act::BaseProcMgr* baseProcMgr = ksys::act::BaseProcMgr::instance();
    textWriter->printf("ksys::act::BaseProcMgr 0x%08x\n", baseProcMgr);
    if(sLastElevator){
        textWriter->printf("sLastElevator 0x%08x\n", sLastElevator);
        //ID
        textWriter->printf("    ID 0x%08x (%02d)\n", sLastElevator->getId(),  sLastElevator->getId() % 30);
        textWriter->printf("    Name %s\n", sLastElevator->getName().cstr());
        textWriter->printf("    State %d\n", sLastElevator->getState());
    }

    

}

}

