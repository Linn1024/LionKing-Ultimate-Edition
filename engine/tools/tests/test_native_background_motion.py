"""Keep Genesis depth rates attached to the authored SNES scenery bands.

The source-row boundaries are documented in docs/background-audit.md. This
tests the production offset function without requiring ROMs or game assets.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NativeBackgroundMotion(unittest.TestCase):
    def test_authored_bands(self):
        compiler = shutil.which("c++")
        if not compiler:
            self.skipTest("C++ compiler unavailable")
        runner = Path(__file__).resolve().parents[2] / "runner"
        source = (runner / "tlk_wide.c").read_text()
        offsets = source[source.index("static int SceneryFloor("):
                         source.index("static unsigned SceneryCustomColor(")]
        harness = r'''
#include <cassert>
static struct { unsigned wrap; } s_cant_wait;
// PRODUCTION
int main() {
    for (int camera : {7, 255, 1023, 2843}) {
        // Every hill pixel, including its tip and bottom shading, shares a rate.
        for (int row=152; row<200; ++row)
            assert(NativeMotionOffset(1,camera,row)==camera/2);
        assert(NativeMotionOffset(1,camera,151)==camera/4);
        // Water continues through the full 248-row SNES panorama.
        for (int row=200; row<248; ++row)
            assert(NativeMotionOffset(1,camera,row)==camera/2+((camera*(row-199))>>7));
        assert(NativeMotionOffset(5,camera,143)==camera/8);
        assert(NativeMotionOffset(5,camera,144)==camera/4);
        assert(NativeMotionOffset(5,camera,239)==camera/4);
        assert(NativeMotionOffset(5,camera,240)==camera/2);
        // Return already has its own SNES raster joins, not the MD joins.
        assert(NativeMotionOffset(8,camera,96)==camera/8);
        for (int row=97; row<153; ++row)
            assert(NativeMotionOffset(8,camera,row)==camera/4);
        assert(NativeMotionOffset(8,camera,153)==camera/2);
        // Keep the complete cloud detail together before the plain band.
        for (int row=0; row<112; ++row)
            assert(NativeMotionOffset(9,camera,row)==camera/2);
        assert(NativeMotionOffset(9,camera,112)==camera/4);
        assert(NativeMotionOffset(9,camera,184)==camera/2);
    }
    s_cant_wait.wrap=512;
    assert(NativeMotionOffset(1,255,152)==767/2);
    // Keep the original signed floor behavior for cameras before an origin.
    assert(SceneryFloor(-1,3)==-1);
    assert(SceneryFloor(-9,3)==-2);
}
'''
        harness = "#include <initializer_list>\n" + harness.replace("// PRODUCTION", offsets)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "test.cpp").write_text(harness)
            binary = path / "test.exe"
            result = subprocess.run([compiler, "-std=c++17", str(path / "test.cpp"),
                                     "-o", str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
