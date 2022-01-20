#include <agl/DrawContext.h>
#include <sead/textwriter.h>

// Functions that are typed correctly and linked, so they can be called
namespace ukinglinks {
/* LinkerHints 0x00b45ae0 _ZN10ukinglinks35agl__utl__DevTools__drawBoundBoxImmEPN3agl11DrawContextEPN4sead10TextWriterEPNS3_7Color4fE _ZN3agl3utl8DevTools15drawBoundBoxImmEPNS_11DrawContextERKN4sead9BoundBox3IfEERKNS4_7Color4fEf */
extern void agl__utl__DevTools__drawBoundBoxImm(agl::DrawContext* drawContext, sead::TextWriter* textWriter, sead::Color4f* color);
/* LinkerHints 0x00b1f868 _ZN10ukinglinks24sead__TextWriter__printfEPN4sead10TextWriterEPKcz sead::TextWriter::printf */
extern void sead__TextWriter__printf(sead::TextWriter* textWriter, char const*, ...);
/* LinkerHints 0x00b1f814 _ZN10ukinglinks27sead__TextWriter__beginDrawEPN4sead10TextWriterE */
extern void sead__TextWriter__beginDraw(sead::TextWriter* textWriter);
/* LinkerHints 0x00b1f848 _ZN10ukinglinks25sead__TextWriter__endDrawEPN4sead10TextWriterE */
extern void sead__TextWriter__endDraw(sead::TextWriter* textWriter);
/* LinkerHints 0x00b1f7d0 _ZN10ukinglinks38sead__TextWriter__setCursorFromTopLeftEPN4sead10TextWriterEPNS0_7Vector2IfEE */
extern void sead__TextWriter__setCursorFromTopLeft(sead::TextWriter* textWriter, sead::Vector2<float>* vec2);
}