param(
    [string]$Python = 'python3.12.exe',
    [int]$Jobs = 8,
    [switch]$Regenerate
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $pythonCommand = (Get-Command $Python -ErrorAction Stop).Source
    & $pythonCommand tools/pride_sprite_catalog.py --header engine/generated/resources/pride_sprite_map.h
    if ($LASTEXITCODE -ne 0) { throw 'Verified sprite source map generation failed' }
    & $pythonCommand tools/pride_hitbox_catalog.py
    if ($LASTEXITCODE -ne 0) { throw 'Verified actor body-bound correspondence generation failed' }
    if (Test-Path '.tools/cargo/bin/cargo.exe') {
        $env:CARGO_HOME = Join-Path $projectRoot '.tools/cargo'
        $env:RUSTUP_HOME = Join-Path $projectRoot '.tools/rustup'
        $env:PATH = (Join-Path $projectRoot '.tools/cargo/bin') + ';' + $env:PATH
    }
    # Git for Windows supplies patch; the generator keeps submodules untouched.
    $gitCommand = (Get-Command git -ErrorAction Stop).Source
    $gitUsr = Join-Path (Split-Path (Split-Path $gitCommand -Parent) -Parent) 'usr/bin'
    if (Test-Path (Join-Path $gitUsr 'patch.exe')) { $env:PATH = $gitUsr + ';' + $env:PATH }
    if ($Regenerate -or !(Test-Path 'engine/generated/snesrecomp/module_registry.c')) {
        # Check for any generated game unit; names are controlled by upstream.
        $units = @(Get-ChildItem 'engine/generated/snesrecomp' -Filter '*_v2.c' -ErrorAction SilentlyContinue)
        if ($Regenerate -or $units.Count -eq 0) {
            & $pythonCommand engine/scripts/generate_snesrecomp.py
            if ($LASTEXITCODE -ne 0) { throw 'ROM code generation failed' }
        }
    }
    New-Item -ItemType Directory -Force '.tools' | Out-Null
    $sdlVersion = '3.4.10'
    $sdlHash = '12b34280415ec8418c864408b93d008a20a6530687ee613d60bfbd20411f2785'
    $sdlSource = Join-Path $projectRoot ".tools/SDL3-$sdlVersion"
    if (!(Test-Path (Join-Path $sdlSource 'CMakeLists.txt'))) {
        $archive = Join-Path $projectRoot ".tools/SDL3-$sdlVersion.tar.gz"
        Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/libsdl-org/SDL/releases/download/release-$sdlVersion/SDL3-$sdlVersion.tar.gz" -OutFile $archive
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLower() -ne $sdlHash) { throw 'SDL checksum mismatch' }
        & tar -xf $archive -C .tools
        if ($LASTEXITCODE -ne 0) { throw 'SDL extraction failed' }
    }
    $sdlCmake = $sdlSource.Replace('\', '/')
    $pythonCmake = $pythonCommand.Replace('\', '/')
    & cmake -S engine -B engine/build-win -G Ninja -DCMAKE_BUILD_TYPE=Release -DTLK_STATIC_SDL=ON -DTLK_USE_CCACHE=OFF -DSNESRECOMP_STATIC_RUNTIME=ON "-DSNESRECOMP_SDL3_SOURCE_DIR=$sdlCmake" "-DPython3_EXECUTABLE=$pythonCmake"
    if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed' }
    & cmake --build engine/build-win --target tlk_sdl tlk_headless tlk_prepare_final_assets tlk_prepare_hud_assets tlk_prepare_sprite_assets tlk_prepare_caption_assets tlk_prepare_checkpoint_assets tlk_prepare_revival_assets tlk_prepare_native_hud_assets tlk_prepare_scene_assets -j $Jobs
    if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
    New-Item -ItemType Directory -Force dist,dist/licenses,dist/assets/fonts,settings | Out-Null
    & $pythonCommand tools/prepare_md_backend.py check
    if ($LASTEXITCODE -ne 0) {
        & powershell -ExecutionPolicy Bypass -File scripts/BuildMDResearch.ps1
        if ($LASTEXITCODE -ne 0) { throw 'MD sound driver library build failed' }
    }
    Copy-Item -LiteralPath '.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll' -Destination engine/build-win/genesis_plus_gx_libretro.dll
    Copy-Item -LiteralPath '.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll' -Destination dist/genesis_plus_gx_libretro.dll
    Copy-Item -LiteralPath '.tools/genesis-plus-gx/LICENSE.txt' -Destination dist/licenses/LICENSE-Genesis-Plus-GX.txt
    Copy-Item -LiteralPath engine/build-win/tlk_sdl.exe -Destination dist/LionKing.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_final_assets.exe -Destination dist/PrepareFinalAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_hud_assets.exe -Destination dist/PrepareHudAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_sprite_assets.exe -Destination dist/PrepareSpriteAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_caption_assets.exe -Destination dist/PrepareCaptionAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_checkpoint_assets.exe -Destination dist/PrepareCheckpointAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_revival_assets.exe -Destination dist/PrepareRevivalAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_native_hud_assets.exe -Destination dist/PrepareNativeHudAssets.exe
    Copy-Item -LiteralPath engine/build-win/tlk_prepare_scene_assets.exe -Destination dist/PrepareSceneAssets.exe
    Copy-Item -Path engine/build-win/assets/shaders -Destination dist/assets -Recurse -Force
    Copy-Item -LiteralPath engine/recomp-ui/assets/common/fonts/LatoLatin-Regular.ttf -Destination dist/assets/fonts/LatoLatin-Regular.ttf
    Copy-Item -LiteralPath engine/LICENSE -Destination dist/licenses/LICENSE-TLKRecomp.txt
    Copy-Item -LiteralPath engine/snesrecomp/LICENSE -Destination dist/licenses/LICENSE-snesrecomp.txt
    Copy-Item -LiteralPath engine/recomp-ui/LICENSE -Destination dist/licenses/LICENSE-recomp-ui.txt
    Copy-Item -Path engine/packaging/LICENSE-*.txt -Destination dist/licenses -Force
    Copy-Item -LiteralPath (Join-Path $sdlSource 'LICENSE.txt') -Destination dist/licenses/LICENSE-SDL3.txt
    $revision = & git -C engine rev-parse HEAD
    @("Upstream TLKRecomp: $revision", 'Local changes: resource tree, Pride Lands MD scenery/cub/enemy/pickup/HUD artwork and palettes, Elephant Graveyard background bands and independent MD main-level themes through Pride Rock, independent original-driver music and mapped effects, original pickup placements and per-cell terrain contacts, independent leaf count/gravity/rustle and cub roar activation/animation, roll/hyena cues and reviewed taunt frames/entry voice, ROM importer/scene cache, native and MD audio/presentation-aware saves, verified in-memory MD driver payload loading, 256/320 viewport and optional MD camera tracking, Windows ABI and save replacement fixes', "Built: $([DateTimeOffset]::Now.ToString('o'))") | Set-Content dist/build-info.txt
    Write-Host 'Built dist/LionKing.exe. Launch Play.cmd or one of the level Mix.cmd launchers.'
} finally { Pop-Location }
