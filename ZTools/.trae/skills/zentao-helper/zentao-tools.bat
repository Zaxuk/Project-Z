@echo off
chcp 936 >nul
title ZenTao Helper - 禅道自动化工具

:MENU
cls
echo.
echo ============================================
echo   ZenTao Helper - 禅道自动化工具
echo ============================================
echo.
echo  [1] 交互式拆解需求
echo  [2] 查看我的需求
echo  [3] 查看未分配的需求
echo  [4] 查看我的任务
echo  [5] 重新登录
echo  [0] 退出
echo.
echo ============================================
echo.

set /p choice="请选择操作 (0-5): "

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
echo  交互式拆解需求
echo ============================================
echo.
echo 提示: 输入 b 或 B 可返回主菜单
echo.

:INPUT_STORY_ID
set /p STORY_ID="请输入需求ID (输入 b 返回): "
if /i "%STORY_ID%"=="b" goto MENU
if "%STORY_ID%"=="" goto INPUT_STORY_ID

:INPUT_GRADE
echo.
echo 请选择需求等级 (默认: A+):
echo   1. A-
echo   2. A
echo   3. A+ (默认)
echo   4. A++
echo   5. B
echo   b. 返回上一步
set /p GRADE_CHOICE="选择 (1-5/b, 直接回车=A+): "

if /i "%GRADE_CHOICE%"=="b" goto INPUT_STORY_ID
if "%GRADE_CHOICE%"=="1" set GRADE=A-
if "%GRADE_CHOICE%"=="2" set GRADE=A
if "%GRADE_CHOICE%"=="3" set GRADE=A+
if "%GRADE_CHOICE%"=="4" set GRADE=A++
if "%GRADE_CHOICE%"=="5" set GRADE=B
if "%GRADE_CHOICE%"=="" set GRADE=A+

:INPUT_PRIORITY
echo.
echo 是否紧急 (默认: 否):
echo   1. 否 (默认)
echo   2. 是
echo   b. 返回上一步
set /p PRIORITY_CHOICE="选择 (1-2/b, 直接回车=否): "

if /i "%PRIORITY_CHOICE%"=="b" goto INPUT_GRADE
if "%PRIORITY_CHOICE%"=="1" set PRIORITY=非紧急
if "%PRIORITY_CHOICE%"=="2" set PRIORITY=紧急
if "%PRIORITY_CHOICE%"=="" set PRIORITY=非紧急

:INPUT_ONLINE_TIME
echo.
echo 请选择需求上线时间 (默认: 下下周周一):
echo   1. 下周周一
echo   2. 下周周四
echo   3. 下下周周一 (默认)
echo   4. 下下周周四
echo   b. 返回上一步
set /p ONLINE_CHOICE="选择 (1-4/b, 直接回车=下下周周一): "

if /i "%ONLINE_CHOICE%"=="b" goto INPUT_PRIORITY
if "%ONLINE_CHOICE%"=="1" set ONLINE_TIME=下周周一
if "%ONLINE_CHOICE%"=="2" set ONLINE_TIME=下周周四
if "%ONLINE_CHOICE%"=="3" set ONLINE_TIME=下下周周一
if "%ONLINE_CHOICE%"=="4" set ONLINE_TIME=下下周周四
if "%ONLINE_CHOICE%"=="" set ONLINE_TIME=下下周周一

:INPUT_ASSIGNED_TO
echo.
set /p ASSIGNED_TO="请输入任务执行人 (默认: zhuxu, 输入 b 返回): "
if /i "%ASSIGNED_TO%"=="b" goto INPUT_ONLINE_TIME
if "%ASSIGNED_TO%"=="" set ASSIGNED_TO=zhuxu

:INPUT_HOURS
echo.
set /p HOURS="请输入任务时长/小时 (默认: 8, 输入 b 返回): "
if /i "%HOURS%"=="b" goto INPUT_ASSIGNED_TO
if "%HOURS%"=="" set HOURS=8

:INPUT_DEADLINE
echo.
echo 请选择截止时间 (默认: 本周周五):
echo   1. 本周周五 (默认)
echo   2. 下周周五
echo   b. 返回上一步
set /p DEADLINE_CHOICE="选择 (1-2/b, 直接回车=本周周五): "

if /i "%DEADLINE_CHOICE%"=="b" goto INPUT_HOURS
if "%DEADLINE_CHOICE%"=="1" set DEADLINE=本周周五
if "%DEADLINE_CHOICE%"=="2" set DEADLINE=下周周五
if "%DEADLINE_CHOICE%"=="" set DEADLINE=本周周五

:CONFIRM
echo.
echo ============================================
echo  确认信息
echo ============================================
echo   需求ID: %STORY_ID%
echo   需求等级: %GRADE%
echo   是否紧急: %PRIORITY%
echo   上线时间: %ONLINE_TIME%
echo   执行人: %ASSIGNED_TO%
echo   任务时长: %HOURS% 小时
echo   截止时间: %DEADLINE%
echo ============================================
echo.
echo  [Y] 确认执行
echo  [N] 取消并返回主菜单
echo  [B] 返回修改
echo.

set /p CONFIRM="请选择 (Y/N/B): "

if /i "%CONFIRM%"=="Y" goto EXECUTE_SPLIT
if /i "%CONFIRM%"=="N" goto MENU
if /i "%CONFIRM%"=="B" goto INPUT_DEADLINE
goto CONFIRM

:EXECUTE_SPLIT
echo.
echo 正在拆解需求 #%STORY_ID%...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('拆解需求#%STORY_ID% 需求等级: %GRADE% 需求优先级: %PRIORITY% 需求上线时间: %ONLINE_TIME% 任务执行人: %ASSIGNED_TO% 任务时长: %HOURS% 小时 任务截止时间: %DEADLINE%'); print(result.get('message', '执行完成'))"

echo.
pause
goto MENU

:QUERY_MY_STORIES
echo.
echo 正在查询我的需求...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('查看我的需求'); print(result.get('message', '执行完成'))"

echo.
pause
goto MENU

:QUERY_UNASSIGNED
echo.
echo 正在查询未分配的需求...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('查看未分配的需求'); print(result.get('message', '执行完成'))"

echo.
pause
goto MENU

:QUERY_MY_TASKS
echo.
echo 正在查询我的任务...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('查看我的任务'); print(result.get('message', '执行完成'))"

echo.
pause
goto MENU

:RELOGIN
echo.
echo 正在重新登录...
echo.

python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('登录禅道'); print(result.get('message', '执行完成'))"

echo.
pause
goto MENU

:EXIT
echo.
echo 感谢使用 ZenTao Helper!
echo.
pause
exit /b 0
