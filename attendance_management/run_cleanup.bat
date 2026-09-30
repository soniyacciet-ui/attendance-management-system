@echo off
cd /d C:\Users\Sonia\Desktop\attendance_management
call python manage.py clearsessions >> logs\cleanup.log 2>&1
echo Cleanup complete at %date% %time% >> logs\cleanup.log
