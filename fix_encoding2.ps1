# Fix mojibake encoding in neurodoc Python files - v2 using string Replace overload

function Fix-MojibakeFile {
    param([string]$FilePath)

    $originalBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $originalText = [System.Text.Encoding]::UTF8.GetString($originalBytes)
    $text = $originalText

    $enc = [System.Text.Encoding]::UTF8

    # Single-codepoint mojibake replacements
    # E9 88 80 -> U+2500 (─ BOX DRAWINGS LIGHT HORIZONTAL)
    $bad_box = $enc.GetString([byte[]]@(0xE9, 0x88, 0x80))
    # E8 84 B3 -> U+00D7 (× MULTIPLICATION SIGN)
    $bad_times = $enc.GetString([byte[]]@(0xE8, 0x84, 0xB3))

    # Two-codepoint mojibake sequences (EE 9B 82 is second part, U+E6C2 PUA)
    $pua_suffix = $enc.GetString([byte[]]@(0xEE, 0x9B, 0x82))

    # E9 88 A5 + EE 9B 82 -> — (em dash U+2014) in most contexts
    $bad_emdash_p1 = $enc.GetString([byte[]]@(0xE9, 0x88, 0xA5))
    # E9 88 AB + EE 9B 82 -> → (right arrow U+2192)
    $bad_arrow_p1 = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAB))
    # E9 88 AE + EE 9B 82 -> >= (greater-than or equal U+2265)
    $bad_geq_p1 = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAE))
    # E9 88 AC + EE 9B 82 -> =>
    $bad_imp_p1 = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAC))
    # E7 B5 97 + EE 9B 82 -> No. (garbled 第)
    $bad_di_p1 = $enc.GetString([byte[]]@(0xE7, 0xB5, 0x97))
    # E9 8F 89 + EE 9B 82 -> (empty, garbled 条)
    $bad_tiao_p1 = $enc.GetString([byte[]]@(0xE9, 0x8F, 0x89))

    # Build two-char combined strings using String concatenation (not char arrays)
    $combined_em = [string]::Concat($bad_emdash_p1, $pua_suffix)
    $combined_arr = [string]::Concat($bad_arrow_p1, $pua_suffix)
    $combined_geq = [string]::Concat($bad_geq_p1, $pua_suffix)
    $combined_imp = [string]::Concat($bad_imp_p1, $pua_suffix)
    $combined_di = [string]::Concat($bad_di_p1, $pua_suffix)
    $combined_tiao = [string]::Concat($bad_tiao_p1, $pua_suffix)

    # Replace single-codepoint patterns first
    $text = $text.Replace($bad_box, [string][char]0x2500)   # ─
    $text = $text.Replace($bad_times, [string][char]0x00D7) # ×

    # Replace two-codepoint patterns
    $text = $text.Replace($combined_arr, [string][char]0x2192)  # →
    $text = $text.Replace($combined_geq, [string][char]0x2265)  # ≥
    $text = $text.Replace($combined_imp, "=>")
    $text = $text.Replace($combined_em, [string][char]0x2014)   # —

    # Article reference patterns (specific ordering matters):
    # 绗?9鈥?2鏉? -> Articles 49-52
    $art_49_52 = [string]::Concat($bad_di_p1, $pua_suffix, "9", $bad_emdash_p1, $pua_suffix, "2", $bad_tiao_p1, $pua_suffix)
    $text = $text.Replace($art_49_52, "Articles 49-52")

    # 绗?7鏉? -> Article 37
    $art_37 = [string]::Concat($bad_di_p1, $pua_suffix, "7", $bad_tiao_p1, $pua_suffix)
    $text = $text.Replace($art_37, "Article 37")

    # 绗?2鏉? -> Article 32
    $art_32 = [string]::Concat($bad_di_p1, $pua_suffix, "2", $bad_tiao_p1, $pua_suffix)
    $text = $text.Replace($art_32, "Article 32")

    # Generic remaining 绗? -> No.
    $text = $text.Replace($combined_di, "No.")
    # Generic remaining 鏉? -> (drop it)
    $text = $text.Replace($combined_tiao, "")

    # Remove BOM if present at start
    if ($text.Length -gt 0 -and [int][char]$text[0] -eq 0xFEFF) {
        $text = $text.Substring(1)
    }

    if ($text -ne $originalText) {
        # Write back without BOM
        $newBytes = $enc.GetBytes($text)
        [System.IO.File]::WriteAllBytes($FilePath, $newBytes)
        Write-Host ("Fixed: " + $FilePath)

        # Report what changed
        $remaining = [regex]::Matches($text, '[-鈀-錀-]').Count
        if ($remaining -gt 0) {
            Write-Host ("  WARNING: " + $remaining + " possibly-garbled chars still remain")
        }
    } else {
        Write-Host ("No changes: " + $FilePath)
    }
}

$files = @(
    'neurodoc/detect.py',
    'neurodoc/generate.py',
    'neurodoc/scan_engine.py',
    'neurodoc/pipeline/kernel_builder.py',
    'neurodoc/dataset_api/factory.py',
    'neurodoc/dataset_api/misc_dataset.py'
)

foreach ($f in $files) {
    Fix-MojibakeFile -FilePath $f
}

Write-Host "Done."
