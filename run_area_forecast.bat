@echo off
REM Check if the virtual environment exists
set VENV_PATH1=.venv\Scripts
set VENV_PATH2=venv\Scripts

REM Check if the virtual environment exists in .venv
if exist "%VENV_PATH1%\activate.bat" (
    set VENV_PATH=%VENV_PATH1%
) else (
    REM Check if the virtual environment exists in venv
    if exist "%VENV_PATH2%\activate.bat" (
        set VENV_PATH=%VENV_PATH2%
    ) else (
        echo Virtual environment not found!
        exit /b 1
    )
)

%VENV_PATH%\python.exe -m ebm %*