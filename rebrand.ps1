# 10x Team - Rebranding Script
# Replaces all 10x Team references with 10x.in branding

$basePath = "C:\Users\Anit\Downloads\10x-Team"

# Define replacements
$replacements = @(
    @{ Old = '10x-team'; New = '10x-team' },
    @{ Old = '10x Team'; New = '10x Team' },
    @{ Old = '10x Team'; New = '10x Team' },
    @{ Old = '10x Team'; New = '10x Team' },
    @{ Old = '10x Team'; New = '10x-team' },
    @{ Old = 'Team 10x.in'; New = 'Team 10x.in' },
    @{ Old = 'anit-1to10x'; New = 'anit-1to10x' },
    @{ Old = 'anit-1to10x'; New = 'anit-1to10x' },
    @{ Old = 'anit-1to10x'; New = 'anit-1to10x' },
    @{ Old = '10x Team.cc'; New = '10x.in' },
    @{ Old = 'docs.10x Team.cc'; New = '10x.in/docs' },
    @{ Old = 'github.com/10x Team/10x-team'; New = 'github.com/anit-1to10x/10x-Team' },
    @{ Old = 'github.com/10x Team/10x Team-engineer'; New = 'github.com/anit-1to10x/10x-Team' },
    @{ Old = 'github.com/10x Team/10x Team'; New = 'github.com/anit-1to10x/10x-Team' },
    @{ Old = 'github.com/10x Team'; New = 'github.com/anit-1to10x' },
    @{ Old = ' standalone |  bundled with 10x Team'; New = 'Developed by Team 10x.in' },
    @{ Old = '**Developed by:** Team 10x.in'; New = '**Developed by:** Team 10x.in' },
    @{ Old = ''; New = '' },
    @{ Old = ''; New = '' },
    @{ Old = '10x Team Discord'; New = '10x.in' },
    @{ Old = '10x Team/discord'; New = '10x.in' }
)

# File extensions to process
$extensions = @('*.md', '*.json', '*.js', '*.cjs', '*.ts', '*.tsx', '*.py', '*.html', '*.css', '*.vue', '*.yaml', '*.yml', '*.sh', '*.ps1')

# Exclude directories
$excludeDirs = @('node_modules', '.git', 'dist', 'build', '.vite')

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  10x Team Rebranding Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$totalFiles = 0
$modifiedFiles = 0

foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path $basePath -Filter $ext -Recurse -File | Where-Object {
        $exclude = $false
        foreach ($dir in $excludeDirs) {
            if ($_.FullName -like "*\$dir\*") {
                $exclude = $true
                break
            }
        }
        -not $exclude
    }

    foreach ($file in $files) {
        $totalFiles++
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($null -eq $content) { continue }

        $originalContent = $content

        foreach ($replacement in $replacements) {
            $content = $content -replace [regex]::Escape($replacement.Old), $replacement.New
        }

        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
            $modifiedFiles++
            Write-Host "  Updated: $($file.FullName)" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Rebranding Complete!" -ForegroundColor Green
Write-Host "  Files scanned: $totalFiles" -ForegroundColor White
Write-Host "  Files modified: $modifiedFiles" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
