@echo off
echo Starting Effort Expense Management System...
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo.
echo Starting Streamlit application...
echo The app will open in your default browser.
echo.
streamlit run streamlit_app.py
pause

