@echo off
cd /d "%~dp0"
chcp 65001 >nul
title ZenTao Helper - 禅道自动化工具
python zentao-tools.py
pause
