param(
    [string]$SnesRom,
    [string]$MdRom,
    [string]$DataDirectory,
    [string]$Player,
    [string]$HudPreparer,
    [string]$SpritePreparer,
    [string]$CaptionPreparer,
    [string]$CheckpointPreparer,
    [string]$RevivalPreparer,
    [string]$NativeHudPreparer,
    [string]$ScenePreparer,
    [switch]$NonInteractive
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
if (!$DataDirectory) { $DataDirectory = Join-Path $projectRoot 'game-data' }
$DataDirectory = [IO.Path]::GetFullPath($DataDirectory)

function Prepare-LionKingPackage {
    param([string]$Preparer,[string]$SourceSwitch,[string]$SourcePath,[string]$Stem,
        [string]$Magic,[int]$Version,[string]$Marker,[string]$SecondSwitch,[string]$SecondPath)
    $stage = Join-Path $DataDirectory ($Stem + '-' + [Guid]::NewGuid().ToString('N') + '.staging')
    try {
        $info = New-Object Diagnostics.ProcessStartInfo
        $info.FileName = $Preparer
        $packageArguments = @($SourceSwitch, $SourcePath)
        if ($SecondSwitch) { $packageArguments += @($SecondSwitch, $SecondPath) }
        $packageArguments += @('--output', $stage)
        $info.Arguments = ($packageArguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
        $info.UseShellExecute = $false
        $info.CreateNoWindow = $true
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        $process = New-Object Diagnostics.Process
        $process.StartInfo = $info
        try {
            if (!$process.Start()) { throw "Cannot start $Stem preparation." }
            $stdout = $process.StandardOutput.ReadToEndAsync()
            $stderr = $process.StandardError.ReadToEndAsync()
            $process.WaitForExit()
            $log = $stdout.Result + $stderr.Result
            [IO.File]::AppendAllText((Join-Path $DataDirectory 'setup-last.log'), $log)
            if ($process.ExitCode -ne 0 -or $log -notmatch $Marker) { throw "$Stem preparation failed. See $DataDirectory\setup-last.log." }
        } finally { $process.Dispose() }
        $bytes = [IO.File]::ReadAllBytes($stage)
        if ($bytes.Length -lt 112 -or [Text.Encoding]::ASCII.GetString($bytes,0,8) -ne $Magic -or
            [BitConverter]::ToUInt32($bytes,8) -ne $Version) { throw 'Preparation tool is outdated. Rebuild it before installing.' }
        $hash = (Get-FileHash -LiteralPath $stage -Algorithm SHA256).Hash.ToLowerInvariant()
        $file = $Stem + '-' + $hash + '.assets'
        $target = Join-Path $DataDirectory $file
        # A failed later step leaves older manifests pointing to their own files.
        if (Test-Path -LiteralPath $target) { [IO.File]::Replace($stage, $target, [NullString]::Value) }
        else { [IO.File]::Move($stage, $target) }
        return [ordered]@{ file=$file; version=$Version; sha256=$hash }
    } finally { if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage } }
}

function Install-LionKingData {
    param([string]$SnesPath, [string]$MdPath, [scriptblock]$Progress)
    if (!$Player) { $Player = Join-Path $projectRoot 'dist/LionKing.exe' }
    if (!$ScenePreparer) { $ScenePreparer = Join-Path $projectRoot 'dist/PrepareSceneAssets.exe' }
    if (!(Test-Path -LiteralPath $ScenePreparer -PathType Leaf)) { throw 'Build the scene asset preparer with scripts/Build.ps1 before installing.' }
    if (!(Test-Path -LiteralPath $player -PathType Leaf)) { throw 'Build the player first with scripts/Build.ps1.' }
    $assetPreparer = Join-Path $projectRoot 'dist/PrepareFinalAssets.exe'
    if (!(Test-Path -LiteralPath $assetPreparer -PathType Leaf)) { throw 'Build the asset preparer with scripts/Build.ps1 before installing.' }
    if (!$HudPreparer) { $HudPreparer = Join-Path $projectRoot 'dist/PrepareHudAssets.exe' }
    if (!(Test-Path -LiteralPath $HudPreparer -PathType Leaf)) { throw 'Build the HUD asset preparer with scripts/Build.ps1 before installing.' }
    if (!$SpritePreparer) { $SpritePreparer = Join-Path $projectRoot 'dist/PrepareSpriteAssets.exe' }
    if (!$CaptionPreparer) { $CaptionPreparer = Join-Path $projectRoot 'dist/PrepareCaptionAssets.exe' }
    if (!(Test-Path -LiteralPath $CaptionPreparer -PathType Leaf)) { throw 'Build the caption asset preparer with scripts/Build.ps1 before installing.' }
    if (!$CheckpointPreparer) { $CheckpointPreparer = Join-Path $projectRoot 'dist/PrepareCheckpointAssets.exe' }
    if (!(Test-Path -LiteralPath $CheckpointPreparer -PathType Leaf)) { throw 'Build the checkpoint asset preparer with scripts/Build.ps1 before installing.' }
    if (!$RevivalPreparer) { $RevivalPreparer = Join-Path $projectRoot 'dist/PrepareRevivalAssets.exe' }
    if (!(Test-Path -LiteralPath $RevivalPreparer -PathType Leaf)) { throw 'Build the revival asset preparer with scripts/Build.ps1 before installing.' }
    if (!$NativeHudPreparer) { $NativeHudPreparer = Join-Path $projectRoot 'dist/PrepareNativeHudAssets.exe' }
    if (!(Test-Path -LiteralPath $NativeHudPreparer -PathType Leaf)) { throw 'Build the native HUD asset preparer with scripts/Build.ps1 before installing.' }
    if (!(Test-Path -LiteralPath $SpritePreparer -PathType Leaf)) { throw 'Build the sprite asset preparer with scripts/Build.ps1 before installing.' }
    $specs = @(
        @{ id='snes'; source=$SnesPath; file='roms/lionking-snes-usa.sfc'; hash='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'; title='SNES USA (unheadered)' },
        @{ id='megadrive'; source=$MdPath; file='roms/lionking-megadrive-world.md'; hash='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'; title='Mega Drive World' }
    )
    # Validate both sources before creating or replacing installed data.
    foreach ($spec in $specs) {
        & $Progress 12 "Verifying $($spec.title)..."
        if (!$spec.source -or !(Test-Path -LiteralPath $spec.source -PathType Leaf)) { throw "Select the $($spec.title) ROM." }
        $spec.source = (Resolve-Path -LiteralPath $spec.source).ProviderPath
        $info = Get-Item -LiteralPath $spec.source
        if ($info.Length -ne 3145728 -or (Get-FileHash -LiteralPath $spec.source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $spec.hash) {
            throw "Unsupported $($spec.title) ROM. This build needs the exact 3 MiB version listed in README.md. Your source file was not changed."
        }
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $DataDirectory 'roms') | Out-Null
    foreach ($spec in $specs) {
        & $Progress 40 "Importing $($spec.title)..."
        $target = Join-Path $DataDirectory $spec.file
        $correct = (Test-Path -LiteralPath $target -PathType Leaf) -and
            ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -eq $spec.hash)
        if (!$correct) {
            $temporary = $target + '.import-' + [Guid]::NewGuid().ToString('N')
            try {
                $inputStream = [IO.File]::OpenRead($spec.source)
                try {
                    $outputStream = [IO.File]::Open($temporary, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                    try { $inputStream.CopyTo($outputStream); $outputStream.Flush($true) } finally { $outputStream.Dispose() }
                } finally { $inputStream.Dispose() }
                if ((Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $spec.hash) { throw 'Imported data verification failed.' }
                if (Test-Path -LiteralPath $target) { [IO.File]::Replace($temporary, $target, [NullString]::Value) }
                else { [IO.File]::Move($temporary, $target) }
            } finally {
                if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
            }
        }
    }
    & $Progress 70 'Preparing decoded scenery and cross-version mappings...'
    $scene = Prepare-LionKingPackage $ScenePreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'scenes' 'TLKSCN01' 3 'resource_cache=prepared' '--md-rom' (Join-Path $DataDirectory $specs[1].file)
    $scene.decoded_scenes = 13
    $scene.verified_background_levels = @(0,1,2,4,5,6,7,8,9,10,11,12,13)
    $scene.background_scope = 'Prepared reviewed scene tables; runtime capabilities govern each supported selection. Decoded scenes alone do not prove complete rendering.'
    $scene.cant_wait_foreground = [ordered]@{ matched=12391; total=12400 }
    $scene.pride_contact_cells = 8000
    & $Progress 82 'Preparing menu artwork and animation images...'
    $menu = Prepare-LionKingPackage $assetPreparer '--md-rom' (Join-Path $DataDirectory $specs[1].file) 'final-menu' 'TLKFMAR1' 10 'final_menu_assets=prepared' '--snes-rom' (Join-Path $DataDirectory $specs[0].file)
    $menu.source = 'megadrive'; $menu.scope = 'final menus, cold-start publisher cards, title opening/ready, Options, independent Sound Test artwork with both original catalogues, and independent cheat/level-select artwork; audio selected separately'
    & $Progress 88 'Preparing native final-life, title and Continue reload data...'
    $native = Prepare-LionKingPackage $assetPreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'final-native' 'TLKFNAT1' 2 'final_native_assets=prepared'
    $native.source = 'snes'; $native.scope = 'native menu bank, nine Continue reloads and ten startup/title payloads'
    $native.payloads = 20
    & $Progress 92 'Preparing title sound data...'
    $titleBank = Prepare-LionKingPackage $assetPreparer '--snes-title-bank' (Join-Path $DataDirectory $specs[0].file) 'title-bank' 'TLKTBK01' 1 'title_bank_assets=prepared'
    $titleBank.source = 'snes'; $titleBank.scope = 'startup sound bank 5 packet program'
    $titleBank.bank = 5; $titleBank.packets = 16
    & $Progress 94 'Preparing HUD tiles...'
    $hud = Prepare-LionKingPackage $HudPreparer '--md-rom' (Join-Path $DataDirectory $specs[1].file) 'hud' 'TLKHUD01' 1 'hud_assets=prepared'
    $hud.source = 'megadrive'; $hud.scope = 'roar and health meters, cub/adult portraits and lives 0-9'
    & $Progress 95 'Preparing sprite images and shared palettes...'
    $sprites = Prepare-LionKingPackage $SpritePreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'sprites' 'TLKSPR01' 2 'sprite_assets=prepared' '--md-rom' (Join-Path $DataDirectory $specs[1].file)
    $sprites.source = 'snes+megadrive'; $sprites.scope = 'Reviewed sprite images, native cub death bank, palettes and prepared gameplay tables. Runtime capabilities govern independent selections; owned images alone do not prove complete rendering.'
    $spriteMetadata = [IO.File]::ReadAllBytes((Join-Path $DataDirectory $sprites.file))
    if ($spriteMetadata.Length -lt 192) { throw 'Prepared sprite header is truncated.' }
    $sprites.mapped_images = [BitConverter]::ToUInt32($spriteMetadata,20)
    $sprites.native_death_images = [BitConverter]::ToUInt32($spriteMetadata,156)
    $sprites.policy_sha256 = [BitConverter]::ToString($spriteMetadata,88,32).Replace('-','').ToLowerInvariant()
    $gameplayBytes = [BitConverter]::ToUInt32($spriteMetadata,164)
    if ($gameplayBytes -lt 16 -or $gameplayBytes -gt $spriteMetadata.Length - 192) { throw 'Prepared gameplay metadata is invalid.' }
    $gameplayOffset = $spriteMetadata.Length - $gameplayBytes
    if ([Text.Encoding]::ASCII.GetString($spriteMetadata,$gameplayOffset,8) -ne 'TLKPRD01') { throw 'Prepared gameplay header is invalid.' }
    $sprites.gameplay_schema = [BitConverter]::ToUInt32($spriteMetadata,$gameplayOffset+8)
    & $Progress 96 'Preparing level caption images...'
    $captions = Prepare-LionKingPackage $CaptionPreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'captions' 'TLKCAP01' 2 'caption_assets=prepared' '--md-rom' (Join-Path $DataDirectory $specs[1].file)
    $captions.source = 'snes+megadrive'; $captions.scope = 'Pride images plus all remaining level/bonus captions and King instruction, exact native text metadata and palettes'
    & $Progress 96 'Preparing checkpoint images...'
    $checkpoints = Prepare-LionKingPackage $CheckpointPreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'checkpoints' 'TLKCHK01' 1 'checkpoint_assets=prepared' '--md-rom' (Join-Path $DataDirectory $specs[1].file)
    $checkpoints.source = 'snes+megadrive'; $checkpoints.scope = 'Pride checkpoint head and collection poses with independent palettes'
    & $Progress 96 'Preparing revival images...'
    $revival = Prepare-LionKingPackage $RevivalPreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'revival' 'TLKREV01' 1 'revival_assets=prepared' '--md-rom' (Join-Path $DataDirectory $specs[1].file)
    $revival.source = 'snes+megadrive'; $revival.scope = 'Pride twelve revival poses and idle continuation'
    & $Progress 96 'Preparing health and roar meter glyphs...'
    $nativeHud = Prepare-LionKingPackage $NativeHudPreparer '--snes-rom' (Join-Path $DataDirectory $specs[0].file) 'native-hud' 'TLKNHUD1' 1 'native_hud_assets=prepared'
    $nativeHud.source = 'snes'; $nativeHud.scope = 'native health and roar meter glyph table'
    & $Progress 97 'Writing installation manifest...'
    $manifest = [ordered]@{
        schema=1
        prepared_utc=[DateTime]::UtcNow.ToString('o')
        original_payloads_retained=$true
        roms=[ordered]@{}
        scene_cache=$scene
        menu_assets=$menu
        native_final_assets=$native
        title_bank_assets=$titleBank
        hud_assets=$hud
        sprite_assets=$sprites
        caption_assets=$captions
        checkpoint_assets=$checkpoints
        revival_assets=$revival
        native_hud_assets=$nativeHud
        player_sha256=(Get-FileHash -LiteralPath $player -Algorithm SHA256).Hash.ToLowerInvariant()
        scene_preparer_sha256=(Get-FileHash -LiteralPath $ScenePreparer -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    foreach ($spec in $specs) { $manifest.roms[$spec.id]=[ordered]@{ file=$spec.file; bytes=3145728; sha256=$spec.hash } }
    $manifestPath = Join-Path $DataDirectory 'install.json'
    $tempManifest = $manifestPath + '.tmp-' + [Guid]::NewGuid().ToString('N')
    try {
        [IO.File]::WriteAllText($tempManifest, ($manifest | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding($false)))
        if (Test-Path -LiteralPath $manifestPath) { [IO.File]::Replace($tempManifest, $manifestPath, [NullString]::Value) }
        else { [IO.File]::Move($tempManifest, $manifestPath) }
    } finally { if (Test-Path -LiteralPath $tempManifest) { Remove-Item -LiteralPath $tempManifest } }
    & $Progress 100 'Ready. Start the game with Play.cmd. Source ROMs and existing saves/settings were preserved.'
    return $manifest
}

if ($NonInteractive -or ($SnesRom -and $MdRom)) {
    $result = Install-LionKingData $SnesRom $MdRom { param($Percent,$Message) Write-Host "$Percent% $Message" }
    $result | ConvertTo-Json -Depth 6
    exit 0
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System.Runtime.InteropServices;
public static class LionKingSetupDpi {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
'@
$null=[LionKingSetupDpi]::SetProcessDPIAware()
[Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object Windows.Forms.Form
$form.Text = 'Lion King PC Setup'
$form.StartPosition = 'CenterScreen'
$form.ClientSize = New-Object Drawing.Size(700,330)
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$description = New-Object Windows.Forms.Label
$description.Text = 'Select your SNES USA and Mega Drive World ROMs. Setup imports all original data and prepares the resources used by the port.'
$description.SetBounds(20,18,660,42)
$form.Controls.Add($description)
$boxes = @()
foreach ($row in 0..1) {
    $label = New-Object Windows.Forms.Label
    $label.Text = @('SNES USA ROM','Mega Drive World ROM')[$row]
    $label.SetBounds(20,(72+$row*63),550,18)
    $form.Controls.Add($label)
    $box = New-Object Windows.Forms.TextBox
    $box.SetBounds(20,(94+$row*63),560,25)
    $candidate = Join-Path $projectRoot (@('Lion King, The (USA).sfc','Lion King, The (World).md')[$row])
    if (!(Test-Path -LiteralPath $candidate)) { $candidate=Join-Path $DataDirectory (@('roms/lionking-snes-usa.sfc','roms/lionking-megadrive-world.md')[$row]) }
    if (Test-Path -LiteralPath $candidate) { $box.Text=$candidate }
    $form.Controls.Add($box);$boxes+=$box
    $browse = New-Object Windows.Forms.Button
    $browse.Text='Browse...';$browse.Tag=$row;$browse.SetBounds(590,(92+$row*63),90,28)
    $browse.Add_Click({
        $dialog=New-Object Windows.Forms.OpenFileDialog
        $dialog.Title='Select original game ROM'
        $dialog.Filter=if($this.Tag -eq 0){'SNES ROM (*.sfc;*.smc)|*.sfc;*.smc|All files (*.*)|*.*'}else{'Mega Drive ROM (*.md;*.bin)|*.md;*.bin|All files (*.*)|*.*'}
        try { if($dialog.ShowDialog($form) -eq 'OK') { $boxes[[int]$this.Tag].Text=$dialog.FileName } } finally { $dialog.Dispose() }
    })
    $form.Controls.Add($browse)
}
$status = New-Object Windows.Forms.Label
$status.Text='Data will be stored in '+$DataDirectory
$status.SetBounds(20,200,660,42);$form.Controls.Add($status)
$bar=New-Object Windows.Forms.ProgressBar
$bar.SetBounds(20,247,660,18);$form.Controls.Add($bar)
$prepare=New-Object Windows.Forms.Button
$prepare.Text='Prepare game data';$prepare.SetBounds(390,282,180,30);$form.Controls.Add($prepare)
$close=New-Object Windows.Forms.Button
$close.Text='Close';$close.SetBounds(590,282,90,30);$close.Add_Click({$form.Close()});$form.Controls.Add($close)
$prepare.Add_Click({
    $prepare.Enabled=$false;$close.Enabled=$false
    try {
        $null=Install-LionKingData $boxes[0].Text $boxes[1].Text { param($Percent,$Message) $bar.Value=$Percent;$status.Text=$Message;[Windows.Forms.Application]::DoEvents() }
        $prepare.Text='Prepare again'
    } catch { $status.Text=$_.Exception.Message;$bar.Value=0 }
    finally { $prepare.Enabled=$true;$close.Enabled=$true }
})
try { $null=$form.ShowDialog() } finally { $form.Dispose() }
