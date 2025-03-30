@echo off
cls
echo Padashetty Coaching Class Website Starter
echo.

if "%1"=="test" goto test
if "%1"=="pdf" goto test_pdf
if "%1"=="deploy" goto deployment_test
if "%1"=="fix" goto fix_database

:normal
echo Starting application in normal mode...
echo.

echo Checking database and uploads directories...
cd backend
python init_db.py

echo.
echo Starting backend server...
start cmd /k "cls && cd backend && echo Starting Flask server on port 5000... && python app.py"

echo.
echo Starting frontend development server...
start cmd /k "cls && cd frontend && echo Starting Vite development server... && npm run dev"

echo.
echo Application is starting up!
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:5173
echo.
echo Admin credentials:
echo Username: pcc
echo Password: pcc@8618
echo.
goto end

:test_pdf
echo Running PDF generation test...
cd backend
python test_pdf.py
goto end

:deployment_test
echo Running deployment test...
python deployment_test.py
goto end

:fix_database
echo Fixing database issues while preserving data...
cd backend
python migrate_db.py
echo.
echo Verifying database and directories...
python init_db.py
echo.
echo Database fix complete!
goto end

:test
echo Running application tests...
echo Testing database reset...
cd backend
python reset_db.py
echo Testing PDF generation...
python test_pdf.py
cd ..
echo Testing deployment...
python deployment_test.py
goto end

:end
