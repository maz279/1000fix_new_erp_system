<#
    Update-Fields.ps1

    python-docx cannot compute a table of contents; it writes the field and
    marks the document "update fields on open". That works for a reader with
    Word, but it means the shipped file shows a placeholder until somebody
    opens it, and it means the page count is unknown to the build.

    This opens each finished guide book once in Word, updates every field and
    every table of contents, repaginates, saves, and reports the real page
    count. Run it after build_business.py.

        powershell -ExecutionPolicy Bypass -File Update-Fields.ps1
        powershell -ExecutionPolicy Bypass -File Update-Fields.ps1 M01
#>
param([string[]]$Only)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dir = Join-Path $here '..\01_Modules\A_Service_Delivery_and_Operations'
$dir = (Resolve-Path $dir).Path

$files = Get-ChildItem -Path $dir -Filter '*.docx' |
         Where-Object { $_.Name -notlike '~$*' }
if ($Only) {
    $files = $files | Where-Object {
        $n = $_.Name
        ($Only | Where-Object { $n -like "$_*" }).Count -gt 0
    }
}
if (-not $files) { Write-Host 'nothing to update'; exit 0 }

# A dying Word instance will hand itself back to the next CreateObject call and
# fail with "RPC server is unavailable". Wait for the process to actually go.
Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
for ($w = 0; $w -lt 40; $w++) {
    if (-not (Get-Process WINWORD -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds 250
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try { $word.Options.CheckSpellingAsYouType = $false } catch {}
try { $word.Options.CheckGrammarAsYouType = $false } catch {}

$results = @()
foreach ($f in $files) {
    $doc = $null
    try {
        $doc = $word.Documents.Open($f.FullName, $false, $false)

        # Order matters. The body fields carry the SEQ counters that number
        # every exhibit and table, so they have to settle before the contents
        # lists are built from them. Updating the lists first and the fields
        # afterwards leaves Word refusing the second pass.
        #
        # Body fields only, too: walking every story range and updating each
        # one forces a repagination per call and on a document with a few
        # hundred SEQ fields it never finishes. The header and footer carry
        # PAGE and NUMPAGES, which Word evaluates at render time regardless.
        $doc.Content.Fields.Update() | Out-Null
        foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
        foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
        $doc.Repaginate()
        # 4 = wdNumberOfPagesInDocument
        $pages = $doc.ComputeStatistics(2)
        $words = $doc.ComputeStatistics(0)
        $doc.Save()
        $results += [pscustomobject]@{
            File = $f.Name; Pages = $pages; Words = $words
        }
        Write-Host ("  {0,-56} {1,4} pages  {2,7:N0} words" -f
                    $f.Name.Substring(0, [Math]::Min(56, $f.Name.Length)),
                    $pages, $words)
    } catch {
        Write-Host ("  {0}  FAILED: {1}" -f $f.Name, $_.Exception.Message)
    } finally {
        if ($doc) { $doc.Close($true) | Out-Null }
    }
}

$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
[GC]::Collect(); [GC]::WaitForPendingFinalizers()

Write-Host ''
Write-Host ("{0} document(s) updated, {1} pages in total" -f
            $results.Count, ($results | Measure-Object -Property Pages -Sum).Sum)
