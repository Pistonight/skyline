#pragma once

#include <extra/nn/svc.h>
#include "types.h"
#include <nn/types.h>

namespace nn::sf::hipc {
void* GetMessageBufferOnTls();

nn::Result InitializeHipcServiceResolution();
nn::Result ConnectToHipcService(nn::svc::Handle*, char const*);
nn::Result FinalizeHipcServiceResolution();

nn::Result SendSyncRequest(nn::svc::Handle, void*, ulong);
nn::Result CloseClientSessionHandle(nn::svc::Handle);

namespace detail {}
};  // namespace nn::sf::hipc