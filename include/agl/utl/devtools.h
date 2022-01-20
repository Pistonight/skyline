#include "types.h"
#include "agl/DrawContext.h"
#include "sead/vector.h"
#include "sead/color.h"

#pragma once

namespace agl {
    namespace utl {
        class DevTools{
            public:
            /* LinkerHints 0x00b4894c _ZN3agl3utl8DevTools12beginDrawImmEPNS_11DrawContextERKN4sead8Matrix34IfEERKNS4_8Matrix44IfEE */
            void static beginDrawImm(agl::DrawContext *,sead::Matrix34<float> const&,sead::Matrix44<float> const&);
            void static drawTriangleImm(agl::DrawContext*, sead::Vector3<float> const&, sead::Vector3<float> const&, sead::Vector3<float> const&, sead::Color4f const&);
            void static drawLineImm(agl::DrawContext*, sead::Vector3<float> const&, sead::Vector3<float> const&, sead::Color4f const&, float);
        };
    };
};