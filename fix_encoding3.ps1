# Fix mojibake encoding - CORRECT version based on actual byte analysis
# Patterns found by xxd analysis:
#   E9 88 B9 E2 82 AC = 鈹€ (two chars: U+9239 U+20AC) -> ─ (U+2500)
#   E9 88 A5 3F       = 鈥? (U+9225 + ?) -> — (em dash U+2014)
#   E9 88 AB 3F       = 鈫? (U+922B + ?) -> → (U+2192)
#   E9 88 AE 3F       = 鈮? (U+922E + ?) -> ≥ (U+2265)
#   E9 88 AC 3F       = 鈬? (U+922C + ?) -> =>
#   E8 84 B3          = 脳 (U+8133) -> × (U+00D7)
#   E7 BB 97 3F       = 绗? (U+7ED7 + ?) -> No. (garbled 第, article number)
#   E9 8F 89 3F       = 鏉? (U+9BC9 + ?) -> "" (garbled 条, article)

function Fix-MojibakeFile {
    param([string]$FilePath)

    $enc = [System.Text.Encoding]::UTF8
    $originalBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $originalText = $enc.GetString($originalBytes)
    $text = $originalText

    # Remove BOM if present
    if ($text.Length -gt 0 -and [int][char]$text[0] -eq 0xFEFF) {
        $text = $text.Substring(1)
    }

    # === Pattern: E9 88 B9 E2 82 AC -> ─ ===
    # U+9239 = encoded by E9 88 B9
    # U+20AC = encoded by E2 82 AC (€ euro sign)
    $p_box_ch1 = $enc.GetString([byte[]]@(0xE9, 0x88, 0xB9))   # U+9239
    $p_euro    = $enc.GetString([byte[]]@(0xE2, 0x82, 0xAC))   # U+20AC (€)
    $pat_box   = [string]::Concat($p_box_ch1, $p_euro)          # 鈹€
    $text = $text.Replace($pat_box, [string][char]0x2500)        # ─

    # === Pattern: E9 88 A5 3F -> — ===
    $p_em      = $enc.GetString([byte[]]@(0xE9, 0x88, 0xA5))   # U+9225
    $pat_em    = [string]::Concat($p_em, "?")                    # 鈥?
    $text = $text.Replace($pat_em, [string][char]0x2014)         # —

    # === Pattern: E9 88 AB 3F -> → ===
    $p_arr     = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAB))   # U+922B
    $pat_arr   = [string]::Concat($p_arr, "?")                   # 鈫?
    $text = $text.Replace($pat_arr, [string][char]0x2192)        # →

    # === Pattern: E9 88 AE 3F -> ≥ ===
    $p_geq     = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAE))   # U+922E
    $pat_geq   = [string]::Concat($p_geq, "?")                   # 鈮?
    $text = $text.Replace($pat_geq, [string][char]0x2265)        # ≥

    # === Pattern: E9 88 AC 3F -> => ===
    $p_imp     = $enc.GetString([byte[]]@(0xE9, 0x88, 0xAC))   # U+922C
    $pat_imp   = [string]::Concat($p_imp, "?")                   # 鈬?
    $text = $text.Replace($pat_imp, "=>")

    # === Pattern: E8 84 B3 -> × ===
    $pat_times = $enc.GetString([byte[]]@(0xE8, 0x84, 0xB3))   # U+8133
    $text = $text.Replace($pat_times, [string][char]0x00D7)      # ×

    # === Article patterns (detect.py specific): ===
    # E7 BB 97 3F = 绗? (garbled 第, "Article")
    $p_di      = $enc.GetString([byte[]]@(0xE7, 0xBB, 0x97))   # U+7ED7
    $pat_di    = [string]::Concat($p_di, "?")                    # 绗?
    # E9 8F 89 3F = 鏉? (garbled 条, "clause/article")
    $p_tiao    = $enc.GetString([byte[]]@(0xE9, 0x8F, 0x89))   # U+9BC9
    $pat_tiao  = [string]::Concat($p_tiao, "?")                  # 鏉?

    # Specific article references: 绗?9鈥?2鏉? -> Articles 49-52
    $art_49_52 = [string]::Concat($pat_di, "9", $pat_em, "2", $pat_tiao)
    $text = $text.Replace($art_49_52, "Articles 49-52")

    # 绗?7鏉? -> Article 37
    $art_37 = [string]::Concat($pat_di, "7", $pat_tiao)
    $text = $text.Replace($art_37, "Article 37")

    # 绗?2鏉? -> Article 32
    $art_32 = [string]::Concat($pat_di, "2", $pat_tiao)
    $text = $text.Replace($art_32, "Article 32")

    # Generic remaining 绗? -> No.
    $text = $text.Replace($pat_di, "No.")
    # Generic remaining 鏉? -> (empty)
    $text = $text.Replace($pat_tiao, "")

    # Also handle any standalone E9 88 A5 (without ?) that might remain from partial fixes
    # This appears in detect.py already fixed, but check
    $p_em_standalone = $enc.GetString([byte[]]@(0xE9, 0x88, 0xA5))
    if ($text.Contains($p_em_standalone)) {
        Write-Host ("  Note: standalone U+9225 found in " + $FilePath)
        # Don't auto-replace standalone - might need context
    }

    if ($text -ne $originalText) {
        $newBytes = $enc.GetBytes($text)
        [System.IO.File]::WriteAllBytes($FilePath, $newBytes)
        Write-Host ("Fixed: " + $FilePath)
    } else {
        Write-Host ("No changes needed: " + $FilePath)
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
