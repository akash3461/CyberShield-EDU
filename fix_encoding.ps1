$files = @(
    "index.html","detector.html","education.html","academy.html",
    "history.html","quiz.html","admin.html","login.html",
    "signup.html","terms.html","developer.html"
)

$utf8NoBom = New-Object System.Text.UTF8Encoding $false

foreach ($f in $files) {
    $path = Join-Path "d:\AI Projects\CyeberShield-EDU\frontend" $f
    if (Test-Path $path) {
        # Read with explicit UTF8 to avoid system default encoding issues
        $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
        # Write back clean UTF8 without BOM
        [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
        Write-Host "Fixed: $f"
    }
}
Write-Host "Done."
