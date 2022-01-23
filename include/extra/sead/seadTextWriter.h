#pragma once

#include <gfx/seadColor.h>
#include <gfx/seadDrawContext.h>
#include <extra/sead/seadVector.h>

namespace sead
{
    class Viewport;
    class Camera;
    class Projection;
    template <typename T> class BoundBox2;

    class TextWriter
    {
        public:
            virtual ~TextWriter();

            void printImpl_(char const*, int, bool, sead::BoundBox2<float>*);
            /* Links KingSymbols150::f_sead__TextWriter__printf _ZN4sead10TextWriter6printfEPKcz (sead::TextWriter::printf) */
            void printf(char const*, ...);
            /* Links KingSymbols150::f_sead__TextWriter__printf _ZN4sead10TextWriter6printfEPKDsz (sead::TextWriter::printf) */
            void printf(char16_t const*, ...);
            void setScaleFromFontHeight(float);
            void beginDraw();
            /* Links KingSymbols150::f_sead__TextWriter__setupGraphics _ZN4sead10TextWriter13setupGraphicsEPNS_11DrawContextE (sead::TextWriter::setupGraphics) */
            static void setupGraphics(sead::DrawContext*);

            sead::Viewport *mViewport;
            sead::Projection *mProjection;
            sead::Camera *mCamera;
            int TextWriter_x20;
            int TextWriter_x24;
            int TextWriter_x28;
            int TextWriter_x2C;
            sead::Vector2<float> mScale;
            sead::Color4f mColor;
            int TextWriter_x48;
            float mLineSpace;
            sead::BoundBox2<float> *mBoundBox2;
            int TextWriter_x58;
            int TextWriter_x5C;
            char16_t *mFormatBuffer;
            int mFormatBufferSize;
            int TextWriter_x6C;
            sead::DrawContext *mDrawContext;
    };
};