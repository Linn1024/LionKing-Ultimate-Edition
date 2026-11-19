# Original MD driver backend and optional reference tools.
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    New-Item -ItemType Directory -Force .tools,build | Out-Null
    $revision='a5834b3df455c49bb97bfaa328c20845831f576b'
    if (!(Test-Path .tools/genesis-plus-gx/.git)) {
        & git clone https://github.com/ekeeke/Genesis-Plus-GX.git .tools/genesis-plus-gx
        if ($LASTEXITCODE -ne 0) { throw 'Reference core clone failed' }
    }
    $actual= & git -C .tools/genesis-plus-gx rev-parse HEAD
    if ($actual -ne $revision) {
        & git -C .tools/genesis-plus-gx fetch origin $revision
        if ($LASTEXITCODE -ne 0) { throw 'Reference revision fetch failed' }
        & git -C .tools/genesis-plus-gx checkout --detach $revision
        if ($LASTEXITCODE -ne 0) { throw 'Reference revision checkout failed' }
    }
    & python3.12.exe tools/prepare_md_backend.py apply
    if ($LASTEXITCODE -ne 0) { throw 'MD continuation patch failed' }
    $gitCommand=(Get-Command git).Source
    $gitUsr=Join-Path (Split-Path (Split-Path $gitCommand -Parent) -Parent) 'usr/bin'
    $env:PATH=$gitUsr+';'+$env:PATH
    Push-Location .tools/genesis-plus-gx
    try {
        & mingw32-make -f Makefile.libretro platform=win HAVE_CHD=0 HAVE_SYS_PARAM=0 HOOK_CPU=1 CPPFLAGS=-fcommon 'SHARED=-shared -static-libgcc -Wl,--export-all-symbols' -j8
        if ($LASTEXITCODE -ne 0) { throw 'Reference core build failed' }
    } finally { Pop-Location }
    & python3.12.exe tools/prepare_md_backend.py package
    if ($LASTEXITCODE -ne 0) { throw 'Matching MD backend source packaging failed' }
    if (!(Test-Path .tools/python32/python.exe)) {
        $zip=Join-Path $projectRoot '.tools/python32.zip'
        Invoke-WebRequest -UseBasicParsing -Uri https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-win32.zip -OutFile $zip
        if ((Get-FileHash $zip).Hash.ToLower() -ne '084b9eb24cb848605c895d05b738fbc2572efc8b4c18c415a824065864a2b853') { throw 'Python archive checksum mismatch' }
        Expand-Archive -LiteralPath $zip -DestinationPath .tools/python32 -Force
    }
    & gcc -shared -O2 -static-libgcc tools/md_trace.c -o build/md_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_start_trace.c -o build/md_start_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Initial-position trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_spawn_trace.c -o build/md_spawn_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Spawn reference trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_scene_trace.c -o build/md_scene_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Scene callback trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_cant_wait_trace.c -o build/md_cant_wait_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Second-level palette trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_death_trace.c -o build/md_death_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Death timeline trace helper build failed' }
    & gcc -shared -O2 -static-libgcc tools/md_revival_trace.c -o build/md_revival_trace.dll
    if ($LASTEXITCODE -ne 0) { throw 'Revival boundary trace helper build failed' }
    Write-Host 'Reference tools ready. Example: .tools/python32/python.exe tools/md_audio_catalog.py'
} finally { Pop-Location }
