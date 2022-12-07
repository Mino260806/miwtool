@echo off

IF "%1"=="" GOTO :Continue

set file=%~n1
set mPath=%~dp1
set mPathScript=%~dp0

python main.py -e "%mPath%%file%"
ren watchface %file%_packed

echo.
echo Resources and JSON in "%mPath%%file%_packed"
echo.
pause

:Continue
IF "%1"=="" echo No bin file given. Usage: %~nx0 path\to\file.bin

