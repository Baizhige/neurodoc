# Fix BOM corruption: BOM was added and consumed the first '"' of the docstring

function Fix-BOM {
    param([string]$FilePath)
    $enc = [System.Text.Encoding]::UTF8
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)

    # Check for UTF-8 BOM (EF BB BF)
    if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        # Remove BOM and prepend the missing '"'
        # The first line should start with '"""' but now starts with '""' (BOM ate one '"')
        $text = $enc.GetString($bytes, 3, $bytes.Length - 3)  # skip BOM

        # Re-add the missing opening quote
        if ($text.StartsWith('""')) {
            $text = '"' + $text
            Write-Host ("Fixed BOM+quote: " + $FilePath)
        } else {
            Write-Host ("Fixed BOM only (no quote corruption): " + $FilePath)
        }

        $newBytes = $enc.GetBytes($text)
        [System.IO.File]::WriteAllBytes($FilePath, $newBytes)
    } else {
        Write-Host ("No BOM: " + $FilePath)
    }
}

$files = @(
    'neurodoc/pipeline/kernel_builder.py',
    'neurodoc/dataset_api/factory.py',
    'neurodoc/dataset_api/misc_dataset.py'
)

foreach ($f in $files) {
    Fix-BOM -FilePath $f
}

Write-Host "Done."
