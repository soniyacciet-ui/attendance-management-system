@echo off
echo ============================================
echo Setting up Automated Attendance Notifications
echo ============================================
echo.

set PROJECT_DIR=C:\Users\Sonia\Desktop\attendance_management
cd /d %PROJECT_DIR%

echo [1/4] Creating task: Weekly Reports (Monday 9 AM)
schtasks /create /tn "Attendance_Weekly_Reports" ^
    /tr "%PROJECT_DIR%\run_weekly.bat" ^
    /sc WEEKLY /d MON /st 09:00 ^
    /f

echo [2/4] Creating task: Daily Alerts (every day 6 PM)
schtasks /create /tn "Attendance_Daily_Alerts" ^
    /tr "%PROJECT_DIR%\run_daily_alerts.bat" ^
    /sc DAILY /st 18:00 ^
    /f

echo [3/4] Creating task: Cleanup (Sunday midnight)
schtasks /create /tn "Attendance_Cleanup" ^
    /tr "%PROJECT_DIR%\run_cleanup.bat" ^
    /sc WEEKLY /d SUN /st 00:00 ^
    /f

echo [4/4] Verifying tasks...
schtasks /query /tn "Attendance_Weekly_Reports"
schtasks /query /tn "Attendance_Daily_Alerts"
schtasks /query /tn "Attendance_Cleanup"

echo.
echo ============================================
echo SETUP COMPLETE
echo ============================================
echo.
echo Tasks scheduled:
echo  - Weekly Reports  -> Every Monday at 9:00 AM
echo  - Daily Alerts    -> Every day at 6:00 PM
echo  - Cleanup         -> Every Sunday at 12:00 AM
echo.
echo Log files:
echo  - %PROJECT_DIR%\logs\weekly.log
echo  - %PROJECT_DIR%\logs\daily.log
echo  - %PROJECT_DIR%\logs\cleanup.log
echo.
pause