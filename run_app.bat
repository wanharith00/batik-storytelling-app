@echo off
echo ========================================
echo Malaysian Batik Storytelling Platform
echo ========================================
echo.
echo Starting the app...
echo.

REM Navigate to the folder where this file is located
cd /d "C:\Users\harith\Desktop\Batik Web App"

REM Run the app
streamlit run batik_web_app.py

echo.
echo App is running at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the app.
pause