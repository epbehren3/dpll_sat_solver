# Run main.py on every .cnf file under satlib_200_860

$folder = "satlib_75_325_sat"

if (-not (Test-Path $folder)) {
    Write-Error "Folder not found: $folder"
    exit 1
}

$files = Get-ChildItem -Path $folder -Recurse -Filter "*.cnf"

if ($files.Count -eq 0) {
    Write-Error "No .cnf files found under $folder"
    exit 1
}

foreach ($file in $files) {
    Write-Host "=== $($file.FullName) ==="
    python main.py $file.FullName
}