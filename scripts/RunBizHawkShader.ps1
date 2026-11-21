param(
    [int]$Frames = 0,
    [switch]$NoPace,
    [switch]$NoAudio,
    [switch]$FpsCounter,
    [int]$PracticeLevel = -1,
    [string]$WindowCapture,
    [string]$SceneCapture
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$settings = Join-Path $projectRoot 'settings/the-best-bizhawk-3xbrz'
[IO.Directory]::CreateDirectory($settings) | Out-Null
$config = Join-Path $settings 'game.ini'
$profile = Join-Path $settings 'resources.ini'
if (!(Test-Path -LiteralPath $config)) {
    $usual = Join-Path $projectRoot 'settings/the-best/game.ini'
    if (Test-Path -LiteralPath $usual) { Copy-Item -LiteralPath $usual -Destination $config }
    else { [IO.File]::WriteAllText($config,"scale = 3`nwindow_size = 960 x 672`n") }
}
if (!(Test-Path -LiteralPath $profile)) {
    $usual = Join-Path $projectRoot 'settings/the-best/resources.ini'
    if (!(Test-Path -LiteralPath $usual)) { $usual = Join-Path $projectRoot 'profiles/the-best.ini' }
    Copy-Item -LiteralPath $usual -Destination $profile
}
$text = [IO.File]::ReadAllText($config)
foreach ($entry in @(@('opengl','1'),@('shader','assets/shaders/bizhawk-3xbrz-linear.glslp'))) {
    $line = $entry[0] + ' = ' + $entry[1]
    $pattern = '(?m)^\s*' + $entry[0] + '\s*=.*$'
    if ([regex]::IsMatch($text,$pattern)) { $text = [regex]::Replace($text,$pattern,$line) }
    else { $text = $text.TrimEnd() + "`n" + $line + "`n" }
}
[IO.File]::WriteAllText($config,$text)
$launch = @{Preset='native';SettingsDirectory=$settings;Frames=$Frames;PracticeLevel=$PracticeLevel}
foreach ($name in @('NoPace','NoAudio','FpsCounter','WindowCapture','SceneCapture')) {
    if ($PSBoundParameters.ContainsKey($name)) { $launch[$name] = $PSBoundParameters[$name] }
}
& (Join-Path $PSScriptRoot 'RunInstalledPreview.ps1') @launch
exit $LASTEXITCODE
