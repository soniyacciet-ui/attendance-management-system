@echo off
cd /d C:\Users\Sonia\Desktop\attendance_management
echo. >> logs\weekly.log
echo ================= %date% %time% ================= >> logs\weekly.log
call python manage.py send_weekly_reports >> logs\weekly.log 2>&1