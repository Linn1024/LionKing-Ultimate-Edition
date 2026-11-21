# BizHawk-style screen effects

3xBRZ Linear reproduces the installed BizHawk two-pass 3xbrz-linear.cgp recipe: 3xBRZ at three times source size, followed by linear filtering. The Cg algorithm was translated to GLSL; original source and its GPL-2.0-or-later notice are in sources/3xbrz.cg. Hyllian vertex mapping notice is retained. Shader files are external, source-readable resources.

HQ2x, BizScanlines and fast bicubic use the GLSL versions included with BizHawk. Original Cg counterparts are preserved in sources/. Bicubic carries Hyllian's MIT notice. BizHawk source: https://github.com/TASEmulators/BizHawk . 3xBRZ source: https://github.com/libretro/common-shaders/tree/master/xbrz . Retain these source files and notices when distributing the effects.

These are selected, tested presets, not a universal Cg/CGP loader. Existing four presets stay available. All need screen effects enabled and a working OpenGL context. Heavy scaling can cost more GPU time on large windows.
