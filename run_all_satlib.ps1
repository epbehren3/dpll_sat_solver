# Run main.py (DPLL + chaff + DLIS) on every .cnf under SATLIB benchmark dirs.
#
# Usage:
#   .\run_all_satlib.ps1                    # all satlib_* directories (recursive)
#   .\run_all_satlib.ps1 -Directory satlib_20_91

param(
    [string] $Directory = ""
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$py = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $py = "python3"
}

$dirs = @()
if ($Directory -ne "") {
    $d = Join-Path $root $Directory
    if (-not (Test-Path -LiteralPath $d -PathType Container)) {
        Write-Error "Not a directory: $d"
        exit 1
    }
    $dirs = @( (Get-Item -LiteralPath $d) )
} else {
    $dirs = @( Get-ChildItem -LiteralPath $root -Directory -Filter "satlib_*" | Sort-Object Name )
    if ($dirs.Count -eq 0) {
        Write-Error "No satlib_* directories under $root. Use -Directory satlib_20_91"
        exit 1
    }
}

$total = 0
foreach ($dir in $dirs) {
    Write-Host "========== $($dir.FullName) =========="
    $files = @( Get-ChildItem -LiteralPath $dir.FullName -Recurse -Filter "*.cnf" | Sort-Object FullName )
    if ($files.Count -eq 0) {
        Write-Warning "No .cnf files under $($dir.FullName)"
        continue
    }
    foreach ($file in $files) {
        $total++
        Write-Host "=== $($file.FullName) ==="
        & $py main.py $file.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "(non-zero exit: $($file.FullName))"
        }
    }
}

Write-Host "Done. Ran main.py on $total .cnf file(s)."
