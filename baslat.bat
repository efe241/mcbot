@echo off
title MCBot Discord Stock & Generator Bot
chcp 65001 > nul
echo ====================================================
echo      MCBot Generator & Stok Botu Başlatılıyor...
echo ====================================================
echo.

python -m pip install -r requirements.txt
echo.
python main.py
pause
