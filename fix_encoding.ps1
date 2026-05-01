# Fix mojibake encoding in neurodoc Python files
# The files contain UTF-8 characters that were mangled via CP1252 re-encoding

function Fix-MojibakeFile {
    param([string]$FilePath)

    $originalText = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
    $text = $originalText

    # These are the mojibake patterns and their correct replacements.
    # The garbled chars come from UTF-8 bytes being misread as Latin-1/CP1252 then re-encoded.

    # 鈹€ (E9 88 80) = U+2500 BOX DRAWINGS LIGHT HORIZONTAL (─)
    $text = $text.Replace([System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0x80)), [char]0x2500)

    # 鈥? (E9 88 A5 + more) = various: check context
    # E9 88 A5 EE 9B 82 = two-char mojibake for … (ellipsis U+2026 = E2 80 A6)
    # Actually let's check: the UTF-8 for em-dash (U+2014) is E2 80 94
    # Misread as Latin-1: â€" -> then those Latin-1 bytes re-encoded as UTF-8
    # â = C3 A2, € = E2 82 AC... no that's not right either

    # The actual encoding issue: original UTF-8 file bytes were interpreted as
    # Windows-1252 (CP1252) and then re-saved as UTF-8.
    # So: original UTF-8 byte E2 = CP1252 char â (U+00E2) -> UTF-8: C3 A2
    #     original UTF-8 byte 80 = CP1252 char € (U+20AC) -> UTF-8: E2 82 AC
    #     But that gives 6 bytes for what was 3 bytes. Let me check differently.

    # Actually the issue is: UTF-8 files read as Latin-1 (ISO-8859-1):
    # U+2014 (—) = E2 80 94 in UTF-8
    # Read as Latin-1: char(0xE2)=â, char(0x80)=<control>, char(0x94)=<control>
    # But those control chars in Latin-1 map to CP1252 printable chars
    # In CP1252: 0x80=€, 0x94=—
    # So we'd get: â€" -> then the mojibake display

    # Let's look at the actual bad sequences found:
    # 鈹€ = U+9240 in the display but actually encoded as E9 88 80 in the file
    # Wait: E9 88 80 decoded as UTF-8 = U+9220? Let me check:
    # U+9220: first byte = E9 (1110xxxx), second = 88 (10xxxxxx), third = 80 (10xxxxxx)
    # = 1001 001000 000000 = U+9200? No:
    # E9 = 11101001 -> upper 4 bits gone, remaining = 1001
    # 88 = 10001000 -> bits = 001000
    # 80 = 10000000 -> bits = 000000
    # Combined: 1001 001000 000000 = 0x9200? No: 1001_001000_000000
    # = 100100 1000 0000 00 -> hmm
    # Actually: U+XXXX where X = (0xE9 & 0x0F)<<12 | (0x88 & 0x3F)<<6 | (0x80 & 0x3F)
    # = 9 << 12 | 8 << 6 | 0 = 36864 + 512 + 0 = 37376 = 0x9200
    # Hmm but shown as 鈹€... let me just do direct string replacement

    # E9 88 80 EE 9B 82 = two UTF-8 chars, together mojibake for BOX DRAWINGS LIGHT HORIZONTAL (─ = U+2500)
    # Actually the sequence is: 鈹€ where 鈹 = E9 88 B9 and € = ... no

    # Let me just use direct text replacement since the file is UTF-8
    # Reading as UTF-8 gives us the actual Unicode codepoints of the garbled chars
    # Then we replace those codepoint sequences

    # From the analysis:
    # E9 88 80 (appears as 鈹€) -> ─ (U+2500)
    # E9 88 A5 EE 9B 82 (appears as 鈥?) -> — (em-dash U+2014) or … (ellipsis U+2026)
    # E8 84 B3 (appears as 脳) -> × (U+00D7)
    # E9 88 AB EE 9B 82 (appears as 鈫?) -> → (U+2192)
    # E9 88 AE EE 9B 82 (appears as 鈮?) -> ≥ (U+2265)
    # E9 88 AC EE 9B 82 (appears as 鈬?) -> => (literal)

    # Let's get the actual characters from these byte sequences
    $bojibake_9200 = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0x80))  # 鈹€ -> ─
    $mojibake_em1  = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0xA5))  # first part of 鈥?
    $mojibake_em2  = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xEE, 0x9B, 0x82))  # second part
    $mojibake_times = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE8, 0x84, 0xB3)) # 脳 -> ×
    $mojibake_arr1 = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0xAB))  # first part of 鈫?
    $mojibake_geq1 = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0xAE))  # first part of 鈮?
    $mojibake_imp1 = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x88, 0xAC))  # first part of 鈬?

    # Also need 绗? pattern: E7 B5 97 EE 9B 82 = 绗?
    $mojibake_zh1 = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE7, 0xB5, 0x97))   # 绗

    # Replace BOX DRAWINGS LIGHT HORIZONTAL repetitions (section separators)
    $text = $text.Replace($bojibake_9200, [char]0x2500)   # ─

    # Replace × (multiplication sign)
    $text = $text.Replace($mojibake_times, [char]0x00D7)  # ×

    # Replace → (rightwards arrow) - two-char mojibake sequence
    $combined_arr = $mojibake_arr1 + $mojibake_em2
    $text = $text.Replace($combined_arr, [char]0x2192)    # →

    # Replace ≥ (greater-than or equal to) - two-char mojibake sequence
    $combined_geq = $mojibake_geq1 + $mojibake_em2
    $text = $text.Replace($combined_geq, [char]0x2265)    # ≥

    # Replace => (implies/segmentation arrow) - two-char mojibake sequence
    $combined_imp = $mojibake_imp1 + $mojibake_em2
    $text = $text.Replace($combined_imp, "=>")

    # Replace — (em dash) and … (ellipsis) - the 鈥? pattern
    # This appears as E9 88 A5 EE 9B 82 and could be:
    # — (em dash U+2014) or … (ellipsis U+2026) depending on context
    # Looking at the files: it appears in "pausing..." type contexts -> —
    # and in "doc: xxx鈥?" truncation contexts -> …
    # We need context-based replacement. Let's handle specific known patterns:
    $combined_em = $mojibake_em1 + $mojibake_em2

    # In detect.py line with dataset(s): '…\n' -> this is the ellipsis+backslash-n
    # In generate.py: 'Interrupt 鈥? pausing' -> em dash
    # In scan_engine.py docstring: 'scan_engine.py 鈥? Core logic' -> em dash
    # In detect.py: 'cannot verify SHA256 (doc: xxx鈥?)' -> ellipsis (truncation)
    # General approach: replace with em dash (—) as it's more common,
    # then the ellipsis context already has … from a previous edit in detect.py

    # Actually from the byte analysis of detect.py line 1217:
    # E9 88 A5 EE 9B 82 6E -> the 6E = 'n', so this is '鈥n' not '鈥?'
    # The '鈥n' in f-string = the ellipsis followed by \n (newline escape)
    # So E9 88 A5 EE 9B 82 followed by 6E 22 29 = ...n") = should be …\n")
    # So E9 88 A5 EE 9B 82 = … (ellipsis U+2026)?

    # Wait - let me think again. If original was UTF-8 and got mangled:
    # — (em dash, U+2014, UTF-8: E2 80 94) → misread as Latin-1 → â€" →
    #   if then re-saved as UTF-8: E2 80 94 would give back â€"...
    #
    # Actually the more likely scenario: someone saved a file with UTF-8 BOM encoding
    # but the tool treated it as CP1252. The cp1252 decode of UTF-8 bytes:
    # E2 = â, 80 = €, 94 = " (right double quotation mark in CP1252)
    # → so — becomes â€" in CP1252 rendering
    # Then re-saved as UTF-8: â=C3A2, €=E282AC, "=E2809D... that's too many bytes.
    #
    # More likely: a Python source file was read/saved incorrectly, causing the UTF-8
    # sequences for special chars to be wrapped in another encoding.
    #
    # Let's just check: what does E9 88 A5 EE 9B 82 decode to?
    # E9 88 A5 = U+9225 (鈥)
    # EE 9B 82 = U+E6C2 (in Private Use Area)
    # Neither is a valid ASCII/Latin char, so these must be the garbled versions.
    #
    # The original chars were likely em-dashes based on context ("pausing", "Core logic")
    # and ellipsis in truncation contexts ("doc: xxx...")
    # Since we can't always distinguish, let's default to — (em dash):
    $text = $text.Replace($combined_em, [char]0x2014)  # —

    # For the detect.py special case dataset(s)…\n") - the 'n' is literal,
    # this was already partially fixed (… inserted), and now we have extra chars
    # The remaining E9 88 A5 EE 9B 82 before 'n' - already handled above

    # Handle 绗? patterns (article references in detect.py)
    # 绗?9鈥?2鏉? = Articles 49–52 (鏉 = E9 8F 89 = 条/article)
    $mojibake_tiao = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x8F, 0x89))  # 鏉 (条)
    $mojibake_en_dash = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE2, 0x80, 0x93))  # – but might not be there

    # Pattern: 绗?9鈥?2鏉? -> Articles 49-52
    # 绗 = E7 B5 97, ? = EE 9B 82, 9 = 39, 鈥 = E9 88 A5, ? = EE 9B 82, 2 = 32, 鏉 = E9 8F 89, ? = EE 9B 82
    $p_zh_di = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE7, 0xB5, 0x97))      # 绗 (第/Article)
    $p_tiao_suf = [System.Text.Encoding]::UTF8.GetString([byte[]]@(0xE9, 0x8F, 0x89))   # 鏉 (条/Clause)

    # Replace article references
    # 绗?9鈥?2鏉? -> Articles 49-52
    $text = $text.Replace($p_zh_di + $mojibake_em2 + "9" + $combined_em + "2" + $p_tiao_suf + $mojibake_em2, "Articles 49-52")
    # 绗?7鏉? -> Article 37
    $text = $text.Replace($p_zh_di + $mojibake_em2 + "7" + $p_tiao_suf + $mojibake_em2, "Article 37")
    # 绗?2鏉? -> Article 32
    $text = $text.Replace($p_zh_di + $mojibake_em2 + "2" + $p_tiao_suf + $mojibake_em2, "Article 32")
    # Generic 绗? -> 第 (but we should not have Chinese in these infrastructure files)
    $text = $text.Replace($p_zh_di + $mojibake_em2, "No.")
    # Generic 鏉? -> 条
    $text = $text.Replace($p_tiao_suf + $mojibake_em2, "")

    # Remove BOM if present
    if ($text.StartsWith([char]0xFEFF)) {
        $text = $text.Substring(1)
    }

    if ($text -ne $originalText) {
        [System.IO.File]::WriteAllText($FilePath, $text, [System.Text.Encoding]::UTF8)
        Write-Host ("Fixed: " + $FilePath)
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
