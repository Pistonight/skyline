#pragma once

#include <gfx/seadTextWriter.h>
#include <KingSystem/ActorSystem/actBaseProcMgr.h>

namespace ksys::skyline {

void Init();
void ComputeDebugData(); 
void RenderDebugScreen(sead::TextWriter* textWriter);

}
