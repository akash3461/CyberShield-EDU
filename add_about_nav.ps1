$files = @(
    "index.html","detector.html","education.html","academy.html",
    "history.html","quiz.html","admin.html","login.html",
    "signup.html","terms.html","developer.html"
)

$utf8NoBom = New-Object System.Text.UTF8Encoding $false

$footerOld  = '<footer class="footer">'
$footerNew  = '<footer class="footer" style="border-top:1px solid var(--glass-border);padding:2rem 0;">'
$footerCopy = '<p>&copy; 2026 CyberShield EDU. Stay Safe, Stay Informed.</p>'
$footerLinks = '<div style="display:flex;gap:1.5rem;"><a href="about.html" style="color:var(--text-secondary);text-decoration:none;font-size:0.9rem;">About</a><a href="terms.html" style="color:var(--text-secondary);text-decoration:none;font-size:0.9rem;">Terms</a><a href="developer.html" style="color:var(--text-secondary);text-decoration:none;font-size:0.9rem;">API</a></div>'
$footerWrap = '<div class="container" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1rem;">'

$aboutNavItem = '                <li><a href="about.html">About</a></li>'

foreach ($f in $files) {
    $path = Join-Path "d:\AI Projects\CyeberShield-EDU\frontend" $f
    if (-not (Test-Path $path)) { Write-Host "Skipped (not found): $f"; continue }

    $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

    # 1. Add About nav link if not present
    if ($text -notmatch 'href="about\.html"') {
        # Insert after the last </li> before </ul></nav>
        $text = $text -replace '((?:<li><a [^>]+>[^<]+</a></li>\s*)+)(</ul>\s*</nav>)', "`$1$aboutNavItem`n            `$2"
    }

    # 2. Upgrade footer: replace simple footer with two-column layout
    # Pattern: <footer class="footer">\n        <p>&copy; ... </p>\n    </footer>
    $text = $text -replace '(?s)<footer class="footer">(\s*<p>[^<]*</p>\s*)</footer>', "<footer class=`"footer`" style=`"border-top:1px solid var(--glass-border);padding:2rem 0;`"><div class=`"container`" style=`"display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1rem;`"><p style=`"margin:0;`">&copy; 2026 CyberShield EDU. Stay Safe, Stay Informed.</p><div style=`"display:flex;gap:1.5rem;`"><a href=`"about.html`" style=`"color:var(--text-secondary);text-decoration:none;font-size:0.9rem;`">About</a><a href=`"terms.html`" style=`"color:var(--text-secondary);text-decoration:none;font-size:0.9rem;`">Terms</a><a href=`"developer.html`" style=`"color:var(--text-secondary);text-decoration:none;font-size:0.9rem;`">API</a></div></div></footer>"

    [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
    Write-Host "Updated: $f"
}

Write-Host "All done."
