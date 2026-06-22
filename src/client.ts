# Save the new client.ts (open in Notepad, copy, paste over existing file)
notepad "$env:USERPROFILE\Downloads\client.ts"
# Ctrl+A → Ctrl+C, then:
$e = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$env:USERPROFILE\Downloads\chainsolve\app\src\client.ts", (Get-Clipboard -Raw), $e)

# Push to GitHub
cd "$env:USERPROFILE\Downloads\chainsolve\app"
git add src/client.ts
git commit -m "fix: TypeScript type errors for Vercel build"
git push