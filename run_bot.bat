@echo off
cd /d "%~dp0"
title Finance Telegram Bot Runner

:loop
echo [%date% %time%] Starting Finance Telegram Bot... >> bot_runner.log 2>&1
echo Starting Finance Telegram Bot...
.\venv\Scripts\python.exe -m bot.main >> bot_runner.log 2>&1
echo [%date% %time%] Bot stopped or crashed. Restarting in 5 seconds... >> bot_runner.log 2>&1
echo Bot stopped. Restarting in 5 seconds...
timeout /t 5 >nul
goto loop
