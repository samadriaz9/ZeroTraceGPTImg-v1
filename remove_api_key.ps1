$content = Get-Content CHATGPT_INTEGRATION.md -Raw
if ($content) {
    $content = $content -replace 'sk-proj[^\s`]+', 'YOUR_API_KEY_HERE'
    $content = $content -replace '```\s*sk-[^\s`]+', '```\nYOUR_API_KEY_HERE'
    Set-Content CHATGPT_INTEGRATION.md -Value $content -NoNewline
}
