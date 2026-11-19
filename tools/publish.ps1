<#
.SYNOPSIS
  Publish "AI Exploration" from this clone to the folder that SharePoint syncs (Windows PowerShell 5.1 or later).

.DESCRIPTION
  Five items, two kinds:
    From git, mirrored (the destination ends up identical, files only it has are deleted):
      2 Ask the Harness Guide, 3 Courses
    Made on this computer, copied only (nothing is deleted at the destination, and a file that is newer
    at the destination is left alone):
      0 MUST READ.pdf, 1 Showcase, 4 Install the harness
  Nothing else in the destination is touched.

  It only previews unless you pass -Apply. The destination path is not in the repository: the first run
  asks for it and keeps it in %USERPROFILE%\.ai-exploration-publish.json.

.PARAMETER Apply
  Really copy (and delete, for the two mirrored folders). Without it nothing changes.
.PARAMETER Pull
  Run "git pull --ff-only" first. Stops if tracked files in the clone were changed.
.PARAMETER Mirror
  Also delete, in the three made-here items, files that are no longer here.
.PARAMETER Yes
  Do not ask "copy to <folder>?". The question about deleting files is always asked.
.PARAMETER Destination
  The synced folder, for this run and the next ones. Default: the saved one, else you are asked.

.EXAMPLE
  .\tools\publish.ps1                 # preview
  .\tools\publish.ps1 -Pull -Apply    # pull, then publish
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Pull,
    [switch]$Mirror,
    [switch]$Yes,
    [string]$Destination
)
$ErrorActionPreference = 'Stop'

$Repo   = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Repo 'AI Exploration'
$Config = Join-Path $env:USERPROFILE '.ai-exploration-publish.json'
$SkipFiles = @('.gitkeep', '~$*', '.DS_Store', 'Thumbs.db', 'desktop.ini')
$SkipDirs  = @('.git')

$FromGit  = @('2 Ask the Harness Guide', '3 Courses')
$FromHere = @(
    @{ Name = '0 MUST READ.pdf';       IsFile = $true  },
    @{ Name = '1 Showcase';            IsFile = $false },
    @{ Name = '4 Install the harness'; IsFile = $false }
)

function Get-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
}

function Get-DestinationFolder {
    $d = $Destination
    if (-not $d -and (Test-Path -LiteralPath $Config)) {
        $d = (Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json).destination
    }
    if (-not $d) {
        $d = Read-Host 'Path of the SharePoint-synced AI Exploration folder'
    }
    $d = "$d".Trim().Trim('"')
    if (-not (Test-Path -LiteralPath $d -PathType Container)) {
        throw "Destination folder not found: $d"
    }
    $dest = Get-FullPath $d
    $src  = Get-FullPath $Source
    if ($dest -ieq $src -or
        $dest.StartsWith($src + '\', [System.StringComparison]::OrdinalIgnoreCase) -or
        $src.StartsWith($dest + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "The destination must be a different folder from the source ($src), and not inside it or around it."
    }
    @{ destination = $dest } | ConvertTo-Json | Set-Content -LiteralPath $Config -Encoding UTF8
    return $dest
}

function Test-Skipped([string]$Name) {
    foreach ($pattern in $SkipFiles) {
        if ($Name -like $pattern) { return $true }
    }
    return $false
}

# Files that are at the destination but not at the source: what a mirror would delete.
function Get-Extras([string]$From, [string]$To) {
    $extras = @()
    if (-not (Test-Path -LiteralPath $To -PathType Container)) { return $extras }
    $toRoot = (Get-FullPath $To) + '\'
    foreach ($f in Get-ChildItem -LiteralPath $To -Recurse -File -Force) {
        if (Test-Skipped $f.Name) { continue }
        $rel = $f.FullName.Substring($toRoot.Length)
        if (-not (Test-Path -LiteralPath (Join-Path $From $rel))) { $extras += $rel }
    }
    return $extras
}

# robocopy: returns its exit code. 0-7 is fine (1 = files copied, 2 = extra files, 4 = mismatches), 8 and up is a failure.
function Invoke-Copy([string]$From, [string]$To, [string[]]$Files, [bool]$Delete, [bool]$KeepNewer) {
    $a = @($From, $To) + $Files
    if ($Delete) { $a += '/MIR' } else { $a += '/E' }
    if ($KeepNewer) { $a += '/XO' }
    $a += '/XF'; $a += $SkipFiles
    $a += '/XD'; $a += $SkipDirs
    $a += @('/R:2', '/W:3', '/NP', '/NJH', '/NJS')
    if (-not $Apply) { $a += '/L' }
    & robocopy @a | Out-Host
    return $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $Source -PathType Container)) { throw "Not found: $Source" }

if ($Pull) {
    $dirty = git -C $Repo status --porcelain --untracked-files=no
    if ($dirty) { throw "The clone has changed tracked files. Commit or discard them first:`n$dirty" }
    git -C $Repo pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'git pull failed.' }
}

$Dest = Get-DestinationFolder
Write-Host ''
Write-Host "From: $Source"
Write-Host "To:   $Dest"
if ($Apply) { Write-Host 'Mode: APPLY' -ForegroundColor Yellow } else { Write-Host 'Mode: preview, nothing is changed. Add -Apply to publish.' -ForegroundColor Cyan }
Write-Host ''

# what the mirrored items would delete
$deleteCount = 0
$mirrored = @($FromGit)
if ($Mirror) { $mirrored += ($FromHere | Where-Object { -not $_.IsFile } | ForEach-Object { $_.Name }) }
foreach ($name in $mirrored) {
    if (-not (Test-Path -LiteralPath (Join-Path $Source $name))) { continue }
    $extras = Get-Extras (Join-Path $Source $name) (Join-Path $Dest $name)
    if ($extras.Count -gt 0) {
        Write-Host "$name : $($extras.Count) file(s) at the destination are not here and will be deleted:" -ForegroundColor Yellow
        $extras | Select-Object -First 15 | ForEach-Object { Write-Host "    $_" }
        if ($extras.Count -gt 15) { Write-Host "    ... and $($extras.Count - 15) more" }
        $deleteCount += $extras.Count
    }
}

if ($Apply) {
    if (-not $Yes) {
        $answer = Read-Host "Copy to $Dest ? (y/N)"
        if ($answer -notmatch '^[yY]') { Write-Host 'Stopped.'; return }
    }
    if ($deleteCount -gt 0) {
        $answer = Read-Host "$deleteCount file(s) will be deleted at the destination. Continue? (y/N)"
        if ($answer -notmatch '^[yY]') { Write-Host 'Stopped.'; return }
    }
}

$failed = @()

foreach ($name in $FromGit) {
    $from = Join-Path $Source $name
    if (-not (Test-Path -LiteralPath $from -PathType Container)) { Write-Host "Skipped (not in the clone): $name" -ForegroundColor Yellow; continue }
    Write-Host "== $name (mirror)"
    $code = Invoke-Copy $from (Join-Path $Dest $name) @() $true $false
    if ($code -ge 8) { $failed += $name }
}

foreach ($item in $FromHere) {
    $path = Join-Path $Source $item.Name
    if (-not (Test-Path -LiteralPath $path)) { Write-Host "Skipped (not here yet): $($item.Name)" -ForegroundColor Yellow; continue }
    Write-Host "== $($item.Name) (copy, keep what is newer at the destination)"
    if ($item.IsFile) {
        $code = Invoke-Copy $Source $Dest @($item.Name) $false $true
    } else {
        $code = Invoke-Copy $path (Join-Path $Dest $item.Name) @() ([bool]$Mirror) $true
    }
    if ($code -ge 8) { $failed += $item.Name }
}

Write-Host ''
if ($failed.Count -gt 0) {
    Write-Host "Some files could not be copied in: $($failed -join ', '). A file open in PowerPoint or Acrobat cannot be copied: close it and run again." -ForegroundColor Red
    exit 1
}
if ($Apply) { Write-Host 'Done. SharePoint now syncs the destination folder.' -ForegroundColor Green }
else { Write-Host 'Nothing was changed. Add -Apply to publish.' -ForegroundColor Cyan }
