@echo off
chcp 65001 >nul
cd /d C:\Users\Sonia\Desktop\attendance_management
echo. >> logs\daily.log
echo ================ %date% %time% ================ >> logs\daily.log
python manage.py auto_notify >> logs\daily.log 2>&1