@echo off
title ZenTao Helper
goto MENU

:MENU
cls
echo.
echo ============================================
echo   ZenTao Helper - Chan Dao Automation Tool
echo ============================================
echo.
echo  [1] Split Story (Interactive)
echo  [2] View My Stories
echo  [3] View Unassigned Stories
echo  [4] View My Tasks
echo  [5] Re-login
echo  [0] Exit
echo.
echo ============================================
echo.
set /p choice=Select operation (0-5): 
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
echo  Split Story (Interactive)
echo ============================================
echo.
echo Tip: Enter b or B to return to main menu
echo.

:INPUT_STORY_ID
set /p STORY_ID=Enter Story ID (enter b to return): 
if /i "%STORY_ID%"=="b" goto MENU
if "%STORY_ID%"=="" goto INPUT_STORY_ID

:INPUT_GRADE
echo.
echo Select story grade (default: A+):
echo   1. A-
echo   2. A
echo   3. A+ (default)
echo   4. A++
echo   5. B
echo   b. Return to previous step
set /p GRADE_CHOICE=Select (1-5/b, press Enter=A+): 
if /i "%GRADE_CHOICE%"=="b" goto INPUT_STORY_ID
if "%GRADE_CHOICE%"=="1" set GRADE=A-
if "%GRADE_CHOICE%"=="2" set GRADE=A
if "%GRADE_CHOICE%"=="3" set GRADE=A+
if "%GRADE_CHOICE%"=="4" set GRADE=A++
if "%GRADE_CHOICE%"=="5" set GRADE=B
if "%GRADE_CHOICE%"=="" set GRADE=A+

:INPUT_PRIORITY
echo.
echo Is urgent? (default: No):
echo   1. No (default)
echo   2. Yes
echo   b. Return to previous step
set /p PRIORITY_CHOICE=Select (1-2/b, press Enter=No): 
if /i "%PRIORITY_CHOICE%"=="b" goto INPUT_GRADE
if "%PRIORITY_CHOICE%"=="1" set PRIORITY=Non-urgent
if "%PRIORITY_CHOICE%"=="2" set PRIORITY=Urgent
if "%PRIORITY_CHOICE%"=="" set PRIORITY=Non-urgent

:INPUT_ONLINE_TIME
echo.
echo Select online time (default: Next next Monday):
echo   1. Next Monday
echo   2. Next Thursday
echo   3. Next next Monday (default)
echo   4. Next next Thursday
echo   b. Return to previous step
set /p ONLINE_CHOICE=Select (1-4/b, press Enter=Next next Monday): 
if /i "%ONLINE_CHOICE%"=="b" goto INPUT_PRIORITY
if "%ONLINE_CHOICE%"=="1" set ONLINE_TIME=Next Monday
if "%ONLINE_CHOICE%"=="2" set ONLINE_TIME=Next Thursday
if "%ONLINE_CHOICE%"=="3" set ONLINE_TIME=Next next Monday
if "%ONLINE_CHOICE%"=="4" set ONLINE_TIME=Next next Thursday
if "%ONLINE_CHOICE%"=="" set ONLINE_TIME=Next next Monday

:INPUT_ASSIGNED_TO
echo.
set /p ASSIGNED_TO=Enter task assignee (default: zhuxu, enter b to return): 
if /i "%ASSIGNED_TO%"=="b" goto INPUT_ONLINE_TIME
if "%ASSIGNED_TO%"=="" set ASSIGNED_TO=zhuxu

:INPUT_HOURS
echo.
set /p HOURS=Enter task hours (default: 8, enter b to return): 
if /i "%HOURS%"=="b" goto INPUT_ASSIGNED_TO
if "%HOURS%"=="" set HOURS=8

:INPUT_DEADLINE
echo.
echo Select deadline (default: This Friday):
echo   1. This Friday (default)
echo   2. Next Friday
echo   b. Return to previous step
set /p DEADLINE_CHOICE=Select (1-2/b, press Enter=This Friday): 
if /i "%DEADLINE_CHOICE%"=="b" goto INPUT_HOURS
if "%DEADLINE_CHOICE%"=="1" set DEADLINE=This Friday
if "%DEADLINE_CHOICE%"=="2" set DEADLINE=Next Friday
if "%DEADLINE_CHOICE%"=="" set DEADLINE=This Friday

:CONFIRM
echo.
echo ============================================
echo  Confirm Information
echo ============================================
echo   Story ID: %STORY_ID%
echo   Grade: %GRADE%
echo   Priority: %PRIORITY%
echo   Online Time: %ONLINE_TIME%
echo   Assignee: %ASSIGNED_TO%
echo   Task Hours: %HOURS% hours
echo   Deadline: %DEADLINE%
echo ============================================
echo.
echo  [Y] Confirm and execute
echo  [N] Cancel and return to main menu
echo  [B] Return to modify
echo.
set /p CONFIRM=Select (Y/N/B): 
if /i "%CONFIRM%"=="Y" goto EXECUTE_SPLIT
if /i "%CONFIRM%"=="N" goto MENU
if /i "%CONFIRM%"=="B" goto INPUT_DEADLINE
goto CONFIRM

:EXECUTE_SPLIT
echo.
echo Splitting story #%STORY_ID%...
echo.
python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('Split story#%STORY_ID% Grade: %GRADE% Priority: %PRIORITY% Online: %ONLINE_TIME% Assignee: %ASSIGNED_TO% Hours: %HOURS% Deadline: %DEADLINE%'); print(result.get('message', 'Done'))"
echo.
pause
goto MENU

:QUERY_MY_STORIES
echo.
echo Querying my stories...
echo.
python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('View my stories'); print(result.get('data', {}).get('message', 'Done'))"
echo.
pause
goto MENU

:QUERY_UNASSIGNED
echo.
echo Querying unassigned stories...
echo.
python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('View unassigned stories'); print(result.get('data', {}).get('message', 'Done'))"
echo.
pause
goto MENU

:QUERY_MY_TASKS
echo.
echo Querying my tasks...
echo.
python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('View my tasks'); print(result.get('data', {}).get('message', 'Done'))"
echo.
pause
goto MENU

:RELOGIN
echo.
echo Re-logging in...
echo.
python -c "import sys; sys.path.insert(0, 'src'); from skill import ZenTaoHelperSkill; skill = ZenTaoHelperSkill(); result = skill.execute('Login Zentao'); print(result.get('message', 'Done'))"
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using ZenTao Helper!
echo.
pause
exit /b 0
