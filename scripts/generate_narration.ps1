param(
    [Parameter(Mandatory = $true)]
    [string]$Config
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech

$configPath = [System.IO.Path]::GetFullPath($Config)
if (-not (Test-Path -LiteralPath $configPath)) { throw "Config not found: $configPath" }
$data = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$projectRoot = Split-Path -Parent $configPath
$outputRoot = if ([System.IO.Path]::IsPathRooted($data.output_dir)) {
    [System.IO.Path]::GetFullPath($data.output_dir)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $projectRoot $data.output_dir))
}
$audioRoot = Join-Path $outputRoot 'audio\raw'
New-Item -ItemType Directory -Force -Path $audioRoot | Out-Null

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice([string]$data.audio.voice)
$synth.Rate = [int]$data.audio.base_rate
$synth.Volume = 100

try {
    foreach ($shot in $data.shots) {
        if ([string]::IsNullOrWhiteSpace([string]$shot.spoken_text)) {
            throw "Shot $($shot.id) has no spoken_text"
        }
        $tag = '{0:D2}' -f [int]$shot.id
        $path = Join-Path $audioRoot ('shot_' + $tag + '.wav')
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
        $synth.SetOutputToWaveFile($path)
        $synth.Speak([string]$shot.spoken_text)
        $synth.SetOutputToNull()
        Get-Item -LiteralPath $path | Select-Object FullName, Length
    }
} finally {
    $synth.Dispose()
}
