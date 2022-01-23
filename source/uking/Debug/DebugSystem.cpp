#include "uking/Debug/DebugSystem.hpp"
#include "uking/Debug/Instances.hpp"

#include <KingSystem/ActorSystem/actBaseProcMgr.h>
#include <skyline/inlinehook/And64InlineHook.hpp>

#include <KingSymbols150.hpp>

void (*BaseProcMgr_RegisterProc_Original)(ksys::act::BaseProcMgr*, ksys::act::BaseProc&);

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
    
    //Hook act::BaseProcMgr::registerProc
    //A64HookFunction(reinterpret_cast<void*>(KingSymbols150::f__ZN4ksys3act11BaseProcMgr12registerProcERNS0_8BaseProcE), reinterpret_cast<void*>(BaseProcMgr_RegisterProc_Hook), reinterpret_cast<void**>(&BaseProcMgr_RegisterProc_Original));
}

void BaseProcMgr_RegisterProc_Hook(act::BaseProcMgr* _this, act::BaseProc& proc){
    if(proc.getName()=="DgnObj_EntranceElevator_A_01"){
        sLastElevator = &proc;
    }
    BaseProcMgr_RegisterProc_Original(_this, proc);
}

void ComputeDebugData(){
    ksys::SystemTimers* systemTimers = ksys::skyline::Global::sSystemTimersInstance;
    if(systemTimers){
        sUnloadCheckFrame = systemTimers->mFrameCounter % 30;
        //if(systemTimers->mFrameCounter > 1800) {
            act::BaseProcMgr* baseProcMgr = ksys::skyline::Global::sBaseProcMgrInstance;
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
    textWriter->printf("Skyline\n");

    
    ksys::SystemTimers* systemTimers = ksys::skyline::Global::sSystemTimersInstance;
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
    
    
    ksys::act::BaseProcMgr* baseProcMgr = ksys::skyline::Global::sBaseProcMgrInstance;
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

