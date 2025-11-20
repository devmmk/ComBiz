@echo off
echo.
echo ComBiz Installer (Windows)
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.x first.
    exit /b 1
)

where pip >nul 2>nul
if errorlevel 1 (
    echo pip is not installed. Please install pip first.
    exit /b 1
)

set "INSTALL_BIN=%USERPROFILE%\AppData\Local\Programs\ComBiz"
set "INSTALL_CONF=%USERPROFILE%\.combiz"

if not exist "%INSTALL_BIN%" mkdir "%INSTALL_BIN%"
if not exist "%INSTALL_CONF%" mkdir "%INSTALL_CONF%"

copy /Y src\combiz.py "%INSTALL_BIN%\combiz.py"
xcopy /Y /E config "%INSTALL_CONF%"

pip install requests

:: Create a combiz.cmd launcher in user path
set "LAUNCHER=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\combiz.cmd"
echo @echo off > "%LAUNCHER%"
echo python "%INSTALL_BIN%\combiz.py" %%* >> "%LAUNCHER%"

echo.
echo ComBiz Installed Successfully!
echo Run combiz from any command prompt.
echo For help, run: combiz --help
echo.
pause
