# PowerShell PDF Generation Script
# Converts all Markdown documentation to PDF format
# Prerequisites: Pandoc must be installed

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PDF Generation Script (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Pandoc is installed
try {
    $pandocVersion = pandoc --version 2>$null | Select-Object -First 1
    if ($pandocVersion) {
        Write-Host "✓ Pandoc found: $pandocVersion" -ForegroundColor Green
    } else {
        throw "Not found"
    }
}
catch {
    Write-Host "✗ ERROR: Pandoc is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation options:" -ForegroundColor Yellow
    Write-Host "1. Chocolatey: choco install pandoc" -ForegroundColor White
    Write-Host "2. Download: https://pandoc.org/installing.html" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "Generating PDFs..." -ForegroundColor Cyan
Write-Host ""

# Create pdfs folder
if (-not (Test-Path "pdfs")) {
    New-Item -ItemType Directory -Name "pdfs" | Out-Null
    Write-Host "Created pdfs folder"
}

# Function to generate PDF
function Generate-PDF {
    param(
        [string]$InputFiles,
        [string]$OutputName,
        [string]$Description,
        [int]$Step,
        [int]$Total
    )
    
    Write-Host "[$Step/$Total] Generating $Description..." -ForegroundColor Cyan
    
    $cmd = "pandoc $InputFiles -o pdfs/$OutputName --pdf-engine=xelatex -V papersize:a4 -V fontsize:11pt --toc"
    
    try {
        Invoke-Expression $cmd
        Write-Host "✓ $Description created" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error creating $Description" -ForegroundColor Red
    }
    Write-Host ""
}

# Generate individual PDFs
Generate-PDF -InputFiles "docs/ERP_RAG_Complete_Guide.md" `
             -OutputName "ERP_RAG_Complete_Guide.pdf" `
             -Description "Complete Guide PDF" `
             -Step 1 -Total 4

Generate-PDF -InputFiles "docs/01-DETAILED-MARKDOWN.md" `
             -OutputName "ERP_RAG_Code_Explanation.pdf" `
             -Description "Code Explanation PDF" `
             -Step 2 -Total 4

Generate-PDF -InputFiles "DEPLOYMENT.md" `
             -OutputName "ERP_RAG_Deployment_Guide.pdf" `
             -Description "Deployment Guide PDF" `
             -Step 3 -Total 4

# Combined PDF
Write-Host "[4/4] Generating Complete Documentation (All in One) PDF..." -ForegroundColor Cyan
try {
    pandoc docs/ERP_RAG_Complete_Guide.md docs/01-DETAILED-MARKDOWN.md DEPLOYMENT.md `
        -o pdfs/ERP_RAG_COMPLETE_DOCUMENTATION.pdf `
        --pdf-engine=xelatex `
        -V papersize:a4 `
        -V fontsize:11pt `
        --toc
    Write-Host "✓ Complete Documentation PDF created" -ForegroundColor Green
}
catch {
    Write-Host "✗ Error creating Complete Documentation PDF" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✓ PDF Generation Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# List generated files
Write-Host "Generated PDFs:" -ForegroundColor Green
Get-ChildItem "pdfs/" -Filter "*.pdf" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  • $($_.Name) ($size MB)" -ForegroundColor White
}

Write-Host ""
Write-Host "All PDFs saved in: pdfs/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to share with friends! 🚀" -ForegroundColor Green
Write-Host ""
