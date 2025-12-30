@echo off
echo ========================================
echo Grammar Checker Backend - Fresh Restart
echo ========================================
echo.

echo Step 1: Cleaning Python cache...
rmdir /s /q __pycache__ 2>nul
rmdir /s /q app\__pycache__ 2>nul
rmdir /s /q app\api\__pycache__ 2>nul
rmdir /s /q app\models\__pycache__ 2>nul
rmdir /s /q app\utils\__pycache__ 2>nul
echo Done!
echo.

echo Step 2: Starting the server...
echo You can test the grammar at: http://localhost:8000/test-grammar
echo.
python -m uvicorn app.main:app --reload --port 8000
