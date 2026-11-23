param(
    [string]$DataDirectory,
    [string]$SettingsDirectory,
    [ValidateSet('pride-development-preview','native','mixed-graphics','pride-lands','next-levels','final-levels')]
    [string]$Preset = 'pride-development-preview',
    [ValidateRange(-1,13)]
    [int]$PracticeLevel = -1,
    [int]$Frames = 0,
    [string]$InputTape,
    [string]$WindowCapture,
    [string]$SceneCapture,
    [string]$AudioCapture,
    [string]$FallbackLog,
    [string]$StateCapture,
    [int]$SaveAt = 0,
    [string]$HashAt,
    [switch]$NoPace,
    [switch]$NoAudio,
    [switch]$FpsCounter,
    [switch]$OriginalTiming,
    [string]$UpdateLog,
    [switch]$Lle
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
try {
    if ($Frames -lt 0) { throw 'Frame count must not be negative.' }
    if ($SaveAt -lt 0 -or ($StateCapture -and (!$SaveAt -or !$Frames -or $SaveAt -gt $Frames)) -or ($SaveAt -and !$StateCapture)) {
        throw 'State capture needs a SaveAt frame between 1 and Frames.'
    }
    if ($PracticeLevel -ge 0 -and $InputTape) { throw 'Practice level selection uses its own controller macro. Use Play.cmd or Play Installed Preview.cmd for input-tape playback.' }
    $package = Join-Path $projectRoot 'dist/installed-preview7122'
    $player = Join-Path $package 'LionKing.exe'
    $packageInfo = Join-Path $package 'package.json'
    if (!(Test-Path -LiteralPath $packageInfo -PathType Leaf)) { throw 'Build/package the installed development preview first. See docs/pride-installed-sprites.md.' }
    $binary = Get-Content -LiteralPath $packageInfo -Raw | ConvertFrom-Json
    foreach ($entry in @(@{path=$player; hash=$binary.player_sha256}, @{path=(Join-Path $package 'genesis_plus_gx_libretro.dll'); hash=$binary.backend_sha256})) {
        if (!(Test-Path -LiteralPath $entry.path -PathType Leaf) -or
            (Get-FileHash -LiteralPath $entry.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.hash) {
            throw 'Development preview files are missing or changed. Rebuild/package the preview.'
        }
    }
    if (!$DataDirectory) { $DataDirectory = Join-Path $projectRoot 'game-data' }
    $DataDirectory = [IO.Path]::GetFullPath($DataDirectory)
    $manifestPath = Join-Path $DataDirectory 'install.json'
    if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw 'Installed game data is missing. Run Setup.cmd first.' }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.schema -ne 1) { throw 'Installed game data is incompatible. Run Setup.cmd again.' }
    function Resolve-PreparedFile {
        param($Spec, [int]$Version = 0)
        if (!$Spec -or !$Spec.file -or !$Spec.sha256 -or ($Version -and $Spec.version -ne $Version)) {
            throw 'Prepared resources are missing or outdated. Run Setup.cmd again.'
        }
        if ([IO.Path]::IsPathRooted($Spec.file)) { throw 'Invalid installed resource path. Run Setup.cmd again.' }
        $path = [IO.Path]::GetFullPath((Join-Path $DataDirectory $Spec.file))
        $prefix = $DataDirectory.TrimEnd([char[]]'\/') + [IO.Path]::DirectorySeparatorChar
        if (!$path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or
            !(Test-Path -LiteralPath $path -PathType Leaf) -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Spec.sha256) {
            throw 'Installed game data is missing or damaged. Run Setup.cmd again.'
        }
        return $path
    }
    $snes = Resolve-PreparedFile $manifest.roms.snes
    $md = Resolve-PreparedFile $manifest.roms.megadrive
    $cache = Resolve-PreparedFile $manifest.scene_cache 3
    $menu = Resolve-PreparedFile $manifest.menu_assets 10
    $native = Resolve-PreparedFile $manifest.native_final_assets 2
    $title = Resolve-PreparedFile $manifest.title_bank_assets 1
    $hud = Resolve-PreparedFile $manifest.hud_assets 1
    $sprites = Resolve-PreparedFile $manifest.sprite_assets 2
    $captions = Resolve-PreparedFile $manifest.caption_assets 2
    $checkpoints = Resolve-PreparedFile $manifest.checkpoint_assets 1
    $revival = Resolve-PreparedFile $manifest.revival_assets 1
    $nativeHud = Resolve-PreparedFile $manifest.native_hud_assets 1
    $spriteBytes = [IO.File]::ReadAllBytes($sprites)
    if ($binary.required_sprite_policy_sha256 -notmatch '^[0-9a-f]{64}$' -or $spriteBytes.Length -lt 192 -or
        [BitConverter]::ToString($spriteBytes,88,32).Replace('-','').ToLowerInvariant() -ne $binary.required_sprite_policy_sha256) {
        throw 'Installed sprite choices are outdated. Run Setup.cmd again.'
    }

    # Create defaults only after the complete installation has been validated.
    if (!$SettingsDirectory) {
        $settingsName = if ($Preset -eq 'pride-development-preview') { 'installed-preview' } else { $Preset }
        $SettingsDirectory = Join-Path $projectRoot ('settings/' + $settingsName)
    }
    $SettingsDirectory = [IO.Path]::GetFullPath($SettingsDirectory)
    New-Item -ItemType Directory -Force -Path $SettingsDirectory | Out-Null
    $config = Join-Path $SettingsDirectory 'game.ini'
    $profile = Join-Path $SettingsDirectory 'resources.ini'
    if (!(Test-Path -LiteralPath $config)) { [IO.File]::WriteAllText($config,"opengl = 0`nscale = 3`n") }
    if (!(Test-Path -LiteralPath $profile)) { Copy-Item -LiteralPath (Join-Path $projectRoot ('profiles/' + $Preset + '.ini')) -Destination $profile }
    $arguments = @('--rom',$snes,'--md-rom',$md,'--asset-cache',$cache,'--final-menu-assets',$menu,
        '--final-native-assets',$native,'--title-bank-assets',$title,'--hud-assets',$hud,'--sprite-assets',$sprites,'--caption-assets',$captions,'--checkpoint-assets',$checkpoints,'--revival-assets',$revival,'--native-hud-assets',$nativeHud,
        '--config',$config,'--resource-profile',$profile)
    if ($Frames) { $arguments += @('--frames',"$Frames",'--no-record') }
    if ($PracticeLevel -ge 0) { $arguments += @('--practice-level',"$PracticeLevel") }
    if ($InputTape) { $arguments += @('--input-polled',[IO.Path]::GetFullPath($InputTape)) }
    if ($WindowCapture) { $arguments += @('--dump-window',[IO.Path]::GetFullPath($WindowCapture)) }
    if ($SceneCapture) { $arguments += @('--dump-scene',[IO.Path]::GetFullPath($SceneCapture)) }
    if ($AudioCapture) { $arguments += @('--wav',[IO.Path]::GetFullPath($AudioCapture),'--wav-seconds','140') }
    if ($StateCapture) { $arguments += @('--save-at',"$SaveAt",[IO.Path]::GetFullPath($StateCapture)) }
    if ($HashAt) { $arguments += @('--hash-at',$HashAt) }
    if ($NoPace) { $arguments += '--no-pace' }
    if ($NoAudio) { $arguments += '--no-audio' }
    if ($Lle) { $arguments += '--lle' }
    $start = New-Object Diagnostics.ProcessStartInfo
    $start.FileName = $player
    $start.Arguments = ($arguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $start.WorkingDirectory = $projectRoot
    if ($FallbackLog) {
        $fallbackPath = [IO.Path]::GetFullPath($FallbackLog)
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fallbackPath)) | Out-Null
        $start.EnvironmentVariables['TLK_FALLBACK_LOG'] = $fallbackPath
        $start.EnvironmentVariables['TLK_FALLBACK_BUILD_HASH'] = $binary.player_sha256
        # Keep the exact selected resources with the latest diagnostic session.
        [IO.File]::WriteAllText(($fallbackPath + '.resources.ini'), [IO.File]::ReadAllText($profile))
        $fallbackSession = [ordered]@{
            started_utc = [DateTime]::UtcNow.ToString('o')
            player_sha256 = $binary.player_sha256
            resource_profile = $profile
            resource_profile_sha256 = (Get-FileHash -LiteralPath $profile -Algorithm SHA256).Hash.ToLowerInvariant()
            log = $fallbackPath
        }
        [IO.File]::WriteAllText(($fallbackPath + '.session.json'), ($fallbackSession | ConvertTo-Json))
    }
    $start.UseShellExecute = $false
    if ($FpsCounter) { $start.EnvironmentVariables['TLK_FPS_COUNTER'] = '1' }
    $start.EnvironmentVariables['TLK_SMOOTH_UPDATES'] = if ($OriginalTiming -or $Lle) { '0' } else { '1' }
    if ($UpdateLog) {
        $updatePath = [IO.Path]::GetFullPath($UpdateLog)
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($updatePath)) | Out-Null
        $start.EnvironmentVariables['TLK_FPS_LOG'] = $updatePath
    }
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $start
    try {
        if (!$process.Start()) { throw 'Cannot start the installed preview.' }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $process.WaitForExit()
        [IO.File]::WriteAllText((Join-Path $SettingsDirectory 'last-launch.log'),$stdout.Result+$stderr.Result)
        $result = $process.ExitCode
    } finally { $process.Dispose() }
    if ($result) { Write-Host "Preview stopped with code $result. See $SettingsDirectory\last-launch.log." }
    exit $result
} catch {
    Write-Host $_.Exception.Message
    exit 8
}
