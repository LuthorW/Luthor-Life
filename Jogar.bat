@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
py -3 --version >/dev/null 2>/dev/null && set "PY=py -3"
if not defined PY python --version >/dev/null 2>/dev/null && set "PY=python"
if not defined PY goto semPython
%PY% -c "import pygame" >/dev/null 2>/dev/null || %PY% -m pip install -r requirements.txt
%PY% main.py
if errorlevel 1 pause
exit /b
:semPython
echo.
echo  Python não foi encontrado neste computador.
echo.
echo  1. Instale o Python 3.13 em https://www.python.org/downloads/
echo  2. Na instalação, marque a opção "Add python.exe to PATH"
echo  3. Depois, abra o Jogar.bat de novo.
echo.
start "" https://www.python.org/downloads/
pause
