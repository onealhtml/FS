@echo off
cd /d "%~dp0"
echo === Moodle Scraper — build do executavel ===
echo.

where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERRO: pip install falhou.
        pause
        exit /b 1
    )
)

echo Gerando o executavel (pode demorar 1-2 min)...
echo.
pyinstaller moodle_scraper.spec --clean
if errorlevel 1 (
    echo.
    echo ERRO ao gerar o executavel.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo  Pronto!
echo  Executavel: dist\moodle_scraper\moodle_scraper.exe
echo  Distribua toda a pasta:  dist\moodle_scraper\
echo =====================================================
echo.
pause
