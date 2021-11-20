@ECHO off
cls
:start
ECHO.
ECHO. UNICORN HYBRID BLACK REPORTER
ECHO. _________________________________
ECHO.
:continue
cd\
cd Studies
cd PythonCollect7
cd Gentask

call conda activate

python Engine\taskselector.py
goto :continue

:end

ECHO.
ECHO.