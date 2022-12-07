@echo off

IF "%1"=="" GOTO :Continue

set file=%~n1
set mPath=%~dp1
set mPathScript=%~dp0

python main.py -dw "%mPath%%file%"
ren watchface.zip %file%_decoded.zip

echo.
echo Resources and JSON in "%mPath%%file%_decoded.zip"
echo.
pause

:Continue
IF "%1"=="" echo No bin file given. Usage: %~nx0 path\to\file.bin

