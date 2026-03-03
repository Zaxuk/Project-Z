#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成正确编码的批处理文件"""

# 批处理文件内容
bat_content = b'''@echo off
chcp 936 >nul
title ZenTao Helper - \u7985\u9053\u81ea\u52a8\u5316\u5de5\u5177

:MENU
cls
echo.
echo ============================================
echo   ZenTao Helper - \u7985\u9053\u81ea\u52a8\u5316\u5de5\u5177
echo ============================================
echo.
echo  [1] \u4ea4\u4e92\u5f0f\u62c6\u89e3\u9700\u6c42
echo  [2] \u67e5\u770b\u6211\u7684\u9700\u6c42
echo  [3] \u67e5\u770b\u672a\u5206\u914d\u7684\u9700\u6c42
echo  [4] \u67e5\u770b\u6211\u7684\u4efb\u52a1
echo  [5] \u91cd\u65b0\u767b\u5f55
echo  [0] \u9000\u51fa
echo.
echo ============================================
echo.

set /p choice="\u8bf7\u9009\u62e9\u64cd\u4f5c (0-5): "

if "%choice%"=="1" goto SPLIT_STORY
if "%choice%"=="2" goto QUERY_MY_STORIES
if "%choice%"=="3" goto QUERY_UNASSIGNED
if "%choice%"=="4" goto QUERY_MY_TASKS
if "%choice%"=="5" goto RELOGIN
if "%choice%"=="0" goto EXIT
goto MENU

:SPLIT_STORY
echo.
echo ============================================
echo  \u4ea4\u4e92\u5f0f\u62c6\u89e3\u9700\u6c42
echo ============================================
echo.
echo \u63d0\u793a: \u8f93\u5165 b \u6216 B \u53ef\u8fd4\u56de\u4e3b\u83dc\u5355
echo.

:INPUT_STORY_ID
set /p STORY_ID="\u8bf7\u8f93\u5165\u9700\u6c42ID (\u8f93\u5165 b \u8fd4\u56de): "
if /i "%STORY_ID%"=="b" goto MENU
if "%STORY_ID%"=="" goto INPUT_STORY_ID

:INPUT_GRADE
echo.
echo \u8bf7\u9009\u62e9\u9700\u6c42\u7b49\u7ea7 (\u9ed8\u8ba4: A+):
echo   1. A-
echo   2. A
echo   3. A+ (\u9ed8\u8ba4)
echo   4. A++
echo   5. B
echo   b. \u8fd4\u56de\u4e0a\u4e00\u6b65
set /p GRADE_CHOICE="\u9009\u62e9 (1-5/b, \u76f4\u63a5\u56de\u8f66=A+): "

if /i "%GRADE_CHOICE%"=="b" goto INPUT_STORY_ID
if "%GRADE_CHOICE%"=="1" set GRADE=A-
if "%GRADE_CHOICE%"=="2" set GRADE=A
if "%GRADE_CHOICE%"=="3" set GRADE=A+
if "%GRADE_CHOICE%"=="4" set GRADE=A++
if "%GRADE_CHOICE%"=="5" set GRADE=B
if "%GRADE_CHOICE%"=="" set GRADE=A+

:INPUT_PRIORITY
echo.
echo \u662f\u5426\u7d27\u6025 (\u9ed8\u8ba4: \u5426):
echo   1. \u5426 (\u9ed8\u8ba4)
echo   2. \u662f
echo   b. \u8fd4\u56de\u4e0a\u4e00\u6b65
set /p PRIORITY_CHOICE="\u9009\u62e9 (1-2/b, \u76f4\u63a5\u56de\u8f66=\u5426): "

if /i "%PRIORITY_CHOICE%"=="b" goto INPUT_GRADE
if "%PRIORITY_CHOICE%"=="1" set PRIORITY=\u975e\u7d27\u6025
if "%PRIORITY_CHOICE%"=="2" set PRIORITY=\u7d27\u6025
if "%PRIORITY_CHOICE%"=="" set PRIORITY=\u975e\u7d27\u6025

:INPUT_ONLINE_TIME
echo.
echo \u8bf7\u9009\u62e9\u9700\u6c42\u4e0a\u7ebf\u65f6\u95f4 (\u9ed8\u8ba4: \u4e0b\u4e0b\u5468\u5468\u4e00):
echo   1. \u4e0b\u5468\u5468\u4e00
echo   2. \u4e0b\u5468\u5468\u56db
echo   3. \u4e0b\u4e0b\u5468\u5468\u4e00 (\u9ed8\u8ba4)
echo   4. \u4e0b\u4e0b\u5468\u5468\u56db
echo   b. \u8fd4\u56de\u4e0a\u4e00\u6b65
set /p ONLINE_CHOICE="\u9009\u62e9 (1-4/b, \u76f4\u63a5\u56de\u8f66=\u4e0b\u4e0b\u5468\u5468\u4e00): "

if /i "%ONLINE_CHOICE%"=="b" goto INPUT_PRIORITY
if "%ONLINE_CHOICE%"=="1" set ONLINE_TIME=\u4e0b\u5468\u5468\u4e00
if "%ONLINE_CHOICE%"=="2" set ONLINE_TIME=\u4e0b\u5468\u5468\u56db
if "%ONLINE_CHOICE%"=="3" set ONLINE_TIME=\u4e0b\u4e0b\u5468\u5468\u4e00
if "%ONLINE_CHOICE%"=="4" set ONLINE_TIME=\u4e0b\u4e0b\u5468\u5468\u56db
if "%ONLINE_CHOICE%"=="" set ONLINE_TIME=\u4e0b\u4e0b\u5468\u5468\u4e00

:INPUT_ASSIGNED_TO
echo.
set /p ASSIGNED_TO="\u8bf7\u8f93\u5165\u4efb\u52a1\u6267\u884c\u4eba (\u9ed8\u8ba4: zhuxu, \u8f93\u5165 b \u8fd4\u56de): "
if /i "%ASSIGNED_TO%"=="b" goto INPUT_ONLINE_TIME
if "%ASSIGNED_TO%"=="" set ASSIGNED_TO=zhuxu

:INPUT_HOURS
echo.
set /p HOURS="\u8bf7\u8f93\u5165\u4efb\u52a1\u65f6\u957f/\u5c0f\u65f6 (\u9ed8\u8ba4: 8, \u8f93\u5165 b \u8fd4\u56de): "
if /i "%HOURS%"=="b" goto INPUT_ASSIGNED_TO
if "%HOURS%"=="" set HOURS=8

:INPUT_DEADLINE
echo.
echo \u8bf7\u9009\u62e9\u622a\u6b62\u65f6\u95f4 (\u9ed8\u8ba4: \u672c\u5468\u5468\u4e94):
echo   1. \u672c\u5468\u5468\u4e94 (\u9ed8\u8ba4)
echo   2. \u4e0b\u5468\u5468\u4e94
echo   b. \u8fd4\u56de\u4e0a\u4e00\u6b65
set /p DEADLINE_CHOICE="\u9009\u62e9 (1-2/b, \u76f4\u63a5\u56de\u8f66=\u672c\u5468\u5468\u4e94): "

if /i "%DEADLINE_CHOICE%"=="b" goto INPUT_HOURS
if "%DEADLINE_CHOICE%"=="1" set DEADLINE=\u672c\u5468\u5468\u4e94
if "%DEADLINE_CHOICE%"=="2" set DEADLINE=\u4e0b\u5468\u5468\u4e94
if "%DEADLINE_CHOICE%"=="" set DEADLINE=\u672c\u5468\u5468\u4e94

:CONFIRM
echo.
echo ============================================
echo  \u786e\u8ba4\u4fe1\u606f
echo ============================================
echo   \u9700\u6c42ID: %STORY_ID%
echo   \u9700\u6c42\u7b49\u7ea7: %GRADE%
echo   \u662f\u5426\u7d27\u6025: %PRIORITY%
echo   \u4e0a\u7ebf\u65f6\u95f4: %ONLINE_TIME%
echo   \u6267\u884c\u4eba: %ASSIGNED_TO%
echo   \u4efb\u52a1\u65f6\u957f: %HOURS% \u5c0f\u65f6
echo   \u622a\u6b62\u65f6\u95f4: %DEADLINE%
echo ============================================
echo.
echo  [Y] \u786e\u8ba4\u6267\u884c
echo  [N] \u53d6\u6d88\u5e76\u8fd4\u56de\u4e3b\u83dc\u5355
echo  [B] \u8fd4\u56de\u4fee\u6539
echo.

set /p CONFIRM="\u8bf7\u9009\u62e9 (Y/N/B): "

if /i "%CONFIRM%"=="Y" goto EXECUTE_SPLIT
if /i "%CONFIRM%"=="N" goto MENU
if /i "%CONFIRM%"=="B" goto INPUT_DEADLINE
goto CONFIRM

:EXECUTE_SPLIT
echo.
echo \u6b63\u5728\u62c6\u89e3\u9700\u6c42 #%STORY_ID%...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('\u62c6\u89e3\u9700\u6c42#%STORY_ID% \u9700\u6c42\u7b49\u7ea7: %GRADE% \u9700\u6c42\u4f18\u5148\u7ea7: %PRIORITY% \u9700\u6c42\u4e0a\u7ebf\u65f6\u95f4: %ONLINE_TIME% \u4efb\u52a1\u6267\u884c\u4eba: %ASSIGNED_TO% \u4efb\u52a1\u65f6\u957f: %HOURS% \u5c0f\u65f6 \u4efb\u52a1\u622a\u6b62\u65f6\u95f4: %DEADLINE%'); print(result.get('message', '\u6267\u884c\u5b8c\u6210'))"

echo.
pause
goto MENU

:QUERY_MY_STORIES
echo.
echo \u6b63\u5728\u67e5\u8be2\u6211\u7684\u9700\u6c42...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('\u67e5\u770b\u6211\u7684\u9700\u6c42'); print(result.get('message', '\u6267\u884c\u5b8c\u6210'))"

echo.
pause
goto MENU

:QUERY_UNASSIGNED
echo.
echo \u6b63\u5728\u67e5\u8be2\u672a\u5206\u914d\u7684\u9700\u6c42...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('\u67e5\u770b\u672a\u5206\u914d\u7684\u9700\u6c42'); print(result.get('message', '\u6267\u884c\u5b8c\u6210'))"

echo.
pause
goto MENU

:QUERY_MY_TASKS
echo.
echo \u6b63\u5728\u67e5\u8be2\u6211\u7684\u4efb\u52a1...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('\u67e5\u770b\u6211\u7684\u4efb\u52a1'); print(result.get('message', '\u6267\u884c\u5b8c\u6210'))"

echo.
pause
goto MENU

:RELOGIN
echo.
echo \u6b63\u5728\u91cd\u65b0\u767b\u5f55...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('\u767b\u5f55\u7985\u9053'); print(result.get('message', '\u6267\u884c\u5b8c\u6210'))"

echo.
pause
goto MENU

:EXIT
echo.
echo \u611f\u8c22\u4f7f\u7528 ZenTao Helper!
echo.
pause
exit /b 0
'''

# 解码Unicode转义序列并写入文件（使用GBK编码）
content = bat_content.decode('unicode_escape')
with open('zentao-tools.bat', 'w', encoding='gbk') as f:
    f.write(content)

print("已生成 zentao-tools.bat (GBK编码)")
