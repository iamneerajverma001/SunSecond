@echo off
title SunSecond GitHub Deployment
echo ========================================================
echo   SunSecond (STDD) - Pushing to GitHub
echo   Target: https://github.com/iamneerajverma001/SunSecond
echo ========================================================
echo.
cd /d "C:\Users\NEERAJ\.gemini\antigravity\scratch\SunSecond"
echo Pushing branch main to GitHub...
echo (If a browser window appears, click 'Sign in' / 'Authorize')
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo   SUCCESS! All files are now on GitHub!
    echo.
    echo   Next Step: Enable GitHub Pages in 30 seconds:
    echo   1. Open: https://github.com/iamneerajverma001/SunSecond/settings/pages
    echo   2. Set Source to 'Deploy from a branch' -> 'main' -> Save
    echo.
    echo   Your live site will be ready at:
    echo   https://iamneerajverma001.github.io/SunSecond/
    echo ========================================================
) else (
    echo ========================================================
    echo   Push failed or was cancelled.
    echo ========================================================
)
echo.
pause
