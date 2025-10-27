@echo off
REM ================================================================================
REM AI-Powered Effort Expense Management System - Launcher Script
REM This script will set up, install dependencies, and launch the application
REM ================================================================================

setlocal enabledelayedexpansion

REM Set color codes for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "PURPLE=[95m"
set "NC=[0m"

cls
echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════════════╗%NC%
echo %BLUE%║         AI-Powered Effort Expense Management System                ║%NC%
echo %BLUE%╚═══════════════════════════════════════════════════════════════════╝%NC%
echo.
echo %CYAN%Welcome to the Effort Expense Management System!%NC%
echo %PURPLE%This script will automatically set up and launch the application.%NC%
echo.

REM ================================================================================
REM Step 1: Check Python Installation
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%Step 1: Checking Python Installation%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Python is not installed!%NC%
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %GREEN%✓ Python found: %PYTHON_VERSION%%NC%
echo.

REM ================================================================================
REM Step 2: Create Virtual Environment
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%Step 2: Setting Up Virtual Environment%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

if exist "venv" (
    echo %CYAN%Virtual environment already exists at: venv%NC%
    set /p RECREATE_VENV="Do you want to recreate it? (y/n): "
    
    if /i "!RECREATE_VENV!"=="y" (
        echo %YELLOW%Removing existing virtual environment...%NC%
        rmdir /s /q venv
        echo %GREEN%✓ Virtual environment removed%NC%
    ) else (
        echo %GREEN%✓ Using existing virtual environment%NC%
        goto skip_venv_create
    )
)

echo %CYAN%Creating virtual environment...%NC%
python -m venv venv

if not exist "venv" (
    echo %RED%✗ Failed to create virtual environment%NC%
    pause
    exit /b 1
)

echo %GREEN%✓ Virtual environment created successfully%NC%
echo.

:skip_venv_create

REM Activate virtual environment
echo %CYAN%Activating virtual environment...%NC%
call venv\Scripts\activate.bat
echo %GREEN%✓ Virtual environment activated%NC%
echo.

REM ================================================================================
REM Step 3: Install Dependencies
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%Step 3: Installing Dependencies%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

echo %CYAN%Upgrading pip...%NC%
python -m pip install --upgrade pip --quiet
echo %GREEN%✓ pip upgraded%NC%
echo.

if exist "requirements.txt" (
    echo %CYAN%Installing required packages...%NC%
    echo %CYAN%This may take a few minutes...%NC%
    echo.
    
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo %RED%✗ Failed to install dependencies%NC%
        echo Please check the error messages above and try again.
        pause
        exit /b 1
    )
    
    echo.
    echo %GREEN%✓ All dependencies installed successfully%NC%
) else (
    echo %RED%✗ requirements.txt not found!%NC%
    pause
    exit /b 1
)
echo.

REM ================================================================================
REM Step 4: Environment Configuration
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%Step 4: Environment Configuration%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

if not exist ".env" (
    echo %CYAN%Creating .env file from template...%NC%
    
    if exist "env_example.txt" (
        copy /y env_example.txt .env >nul
        echo %GREEN%✓ .env file created from template%NC%
        echo %YELLOW%⚠ Please edit .env file with your credentials (optional)%NC%
    ) else (
        echo %YELLOW%⚠ env_example.txt not found. Creating empty .env file...%NC%
        type nul > .env
    )
) else (
    echo %CYAN%.env file already exists%NC%
)
echo.

REM ================================================================================
REM Step 5: Check Application Files
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%Step 5: Checking Application Files%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

set MISSING_FILES=0

if exist "streamlit_app.py" (
    echo %GREEN%✓ Found: streamlit_app.py%NC%
) else (
    echo %RED%✗ Missing: streamlit_app.py%NC%
    set /a MISSING_FILES+=1
)

if exist "data_processor.py" (
    echo %GREEN%✓ Found: data_processor.py%NC%
) else (
    echo %RED%✗ Missing: data_processor.py%NC%
    set /a MISSING_FILES+=1
)

if exist "catboost_model.py" (
    echo %GREEN%✓ Found: catboost_model.py%NC%
) else (
    echo %RED%✗ Missing: catboost_model.py%NC%
    set /a MISSING_FILES+=1
)

if exist "config.py" (
    echo %GREEN%✓ Found: config.py%NC%
) else (
    echo %RED%✗ Missing: config.py%NC%
    set /a MISSING_FILES+=1
)

if %MISSING_FILES% GTR 0 (
    echo.
    echo %RED%✗ %MISSING_FILES% required file(s) are missing!%NC%
    pause
    exit /b 1
)
echo.

REM ================================================================================
REM Step 6: Display System Information
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %BLUE%System Information%NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

echo %CYAN%Application Details:%NC%
echo   • Python Version: %PYTHON_VERSION%
echo   • Virtual Environment: venv
echo   • Working Directory: %CD%
echo.

echo %CYAN%Key Features:%NC%
echo   • AI-powered effort expense prediction
echo   • CatBoost machine learning model
echo   • Data visualization and analysis
echo   • Microsoft 365 integration (optional)
echo   • Automated notification system
echo.

REM ================================================================================
REM Step 7: Launch Application
REM ================================================================================

echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %GREEN%                      🎉 Setup Complete!                          %NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.
echo %GREEN%All systems ready! Launching the application...%NC%
echo.
echo %CYAN%The application will open in your default browser%NC%
echo %CYAN%If it doesn't open automatically, go to: http://localhost:8501%NC%
echo.
echo %YELLOW%Press Ctrl+C to stop the application%NC%
echo.

REM Wait a moment before launching
timeout /t 2 /nobreak >nul

echo %CYAN%Starting Streamlit application...%NC%
echo.
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %GREEN%                   Application is starting...                   %NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

REM Run the Streamlit app
streamlit run streamlit_app.py --server.headless true

echo.
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo %CYAN%                         Application Stopped                     %NC%
echo %BLUE%════════════════════════════════════════════════════════════════%NC%
echo.

set /p RESTART="Do you want to restart the application? (y/n): "

if /i "!RESTART!"=="y" (
    goto :eof
    call "%~f0"
) else (
    echo.
    echo %CYAN%Thank you for using the Effort Expense Management System!%NC%
    echo.
    pause
)

