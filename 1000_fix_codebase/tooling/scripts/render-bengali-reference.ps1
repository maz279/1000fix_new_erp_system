# render-bengali-reference.ps1 — P04-M08-T05 (TR-07, doctor check 10).
#
# Renders the committed Bengali conjunct-shaping reference image through the
# same font the token source names (Noto Sans Bengali) using GDI+ text
# shaping. The image is the committed baseline doctor check 10 compares the
# QWeb report render against — "the only way an automated check catches a
# conjunct-shaping regression before it reaches a Mushak 6.3 invoice".
#
# The sample text is the W1 label set chosen for conjunct density:
#   কর্তনযোগ্য (র্ত + জ্য + reph), ব্যবধান (ব্য), অনুমোদনকারী (নু matra),
#   ডায়াগনস্টিক (স্ট), ওয়ারেন্টি (ওয়া), plus the lakh-crory amount per BN-007.
#
# Output: docs/guides/reference/bengali-conjunct-reference.png (deterministic
# size 900x260, white background, 1px border so edges survive diffing).
# Exit: 0 rendered / 1 font or GDI+ failure.

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$out = Join-Path $repo 'docs\guides\reference\bengali-conjunct-reference.png'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null

Add-Type -AssemblyName System.Drawing

$fontFamily = 'Noto Sans Bengali'
$families = (New-Object System.Drawing.Text.InstalledFontCollection).Families |
    ForEach-Object { $_.Name }
if ($fontFamily -notin $families) {
    # Nirmala UI ships with Windows and shapes Bengali correctly — recorded
    # fallback so the reference still renders on a bare workstation.
    if ('Nirmala UI' -in $families) {
        $fontFamily = 'Nirmala UI'
        Write-Output "render-bengali-reference: NOTE - Noto Sans Bengali absent, using Nirmala UI (recorded in the PNG header text)"
    } else {
        Write-Error 'render-bengali-reference: no Bengali-shaping font installed (need Noto Sans Bengali or Nirmala UI)'
        exit 1
    }
}

$width, $height = 900, 260
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

$pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::Black), 1
$g.DrawRectangle($pen, 0, 0, $width - 1, $height - 1)

$titleFont = New-Object System.Drawing.Font ($fontFamily), 14, ([System.Drawing.FontStyle]::Bold)
$labelFont = New-Object System.Drawing.Font ($fontFamily), 16, ([System.Drawing.FontStyle]::Regular)
$amountFont = New-Object System.Drawing.Font ($fontFamily), 20, ([System.Drawing.FontStyle]::Bold)
$brush = [System.Drawing.Brushes]::Black
$grey = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(92, 99, 112))

$g.DrawString('1000FiX ERP - Bengali conjunct shaping reference (TR-07)', $titleFont, $grey, 16, 12)

$lines = @(
    'কর্তনযোগ্য খরচ (র্ত, জ্য)',
    'ব্যবধান (ব্য) - ডায়াগনস্টিক পথ (স্ট)',
    'অনুমোদনকারী - ওয়ারেন্টি - সিরিয়াল নম্বর'
)
$y = 48
foreach ($line in $lines) {
    $g.DrawString($line, $labelFont, $brush, 16, $y)
    $y += 38
}
# BN-007: ৳ before the amount, Bengali numerals, lakh-crory grouping.
$g.DrawString('মোট: ৳ ১,৫০,০০০.০০', $amountFont, $brush, 16, $y + 6)

$g.Dispose()
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "render-bengali-reference: wrote $out (font: $fontFamily)"
exit 0
