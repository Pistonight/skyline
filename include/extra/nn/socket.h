//Extra functions not included in the original nn/socket

#pragma once

#include <sys/socket.h>

#include "types.h"
#include <nn/socket.h>

namespace nn {
namespace socket {
    u32 Bind(s32 socket, const sockaddr* addr, u32 addrLen);
    u32 Listen(s32 socket, s32 backlog);
    u32 Accept(s32 socket, sockaddr* addrOut, u32* addrLenOut);
};  // namespace socket
};  // namespace nn