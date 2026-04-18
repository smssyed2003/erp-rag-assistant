@echo off
REM Quick PDF Generation Script for ERP RAG Documentation
REM This script converts all markdown documentation to PDF format
REM Prerequisites: Pandoc must be installed (https://pandoc.org/installing.html)

echo.
echo ======================================
echo PDF Generation Script
echo ======================================
echo.

REM Check if Pandoc is installed
where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Pandoc is not installed!
    echo.
    echo Installation options:
    echo 1. Chocolatey: choco install pandoc
    echo 2. Download: https://pandoc.org/installing.html
    echo.
    pause
    exit /b 1
)

echo ✓ Pandoc found!
echo.
echo Generating PDFs...
echo.

REM Create pdfs folder
if not exist "pdfs" mkdir pdfs

REM Generate Individual PDFs
echo [1/4] Generating Complete Guide PDF...
pandoc docs/ERP_RAG_Complete_Guide.md ^
  -o pdfs/ERP_RAG_Complete_Guide.pdf ^
  --pdf-engine=xelatex ^
  -V papersize:a4 ^
  -V fontsize:11pt ^
  --toc
if %errorlevel% equ 0 (echo ✓ Complete Guide PDF created) else (echo ✗ Error creating Complete Guide PDF)

echo.
echo [2/4] Generating Code Explanation PDF...
pandoc docs/01-DETAILED-MARKDOWN.md ^
  -o pdfs/ERP_RAG_Code_Explanation.pdf ^
  --pdf-engine=xelatex ^
  -V papersize:a4
if %errorlevel% equ 0 (echo ✓ Code Explanation PDF created) else (echo ✗ Error)

echo.
echo [3/4] Generating Deployment Guide PDF...
pandoc DEPLOYMENT.md ^
  -o pdfs/ERP_RAG_Deployment_Guide.pdf ^
  --pdf-engine=xelatex ^
  -V papersize:a4
if %errorlevel% equ 0 (echo ✓ Deployment Guide PDF created) else (echo ✗ Error)

echo.
echo [4/4] Generating Complete Documentation (All in One) PDF...
pandoc docs/ERP_RAG_Complete_Guide.md ^
       docs/01-DETAILED-MARKDOWN.md ^
       DEPLOYMENT.md ^
  -o pdfs/ERP_RAG_COMPLETE_DOCUMENTATION.pdf ^
  --pdf-engine=xelatex ^
  -V papersize:a4 ^
  --toc
if %errorlevel% equ 0 (echo ✓ Complete Documentation PDF created) else (echo ✗ Error)

echo.
echo ======================================
echo ✓ PDF Generation Complete!
echo ======================================
echo.
echo Generated PDFs are in: pdfs/
echo.
echo Files created:
echo - ERP_RAG_Complete_Guide.pdf
echo - ERP_RAG_Code_Explanation.pdf
echo - ERP_RAG_Deployment_Guide.pdf
echo - ERP_RAG_COMPLETE_DOCUMENTATION.pdf
echo.
pause
