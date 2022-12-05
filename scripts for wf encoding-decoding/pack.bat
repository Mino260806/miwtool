@echo off

IF "%1"=="" GOTO :Continue

set file=%~n1
set mPath=%~dp1
set mPathScript=%~dp0

python C:\Temp\RedmiWatch2SOFT\miwtool-main\main.py --encode "%mPath%%file%" --output "C:\Temp\RedmiWatch2SOFT\!WacthFaces\input\%file%_packed" -ce little

echo.
echo Resources and JSON in "C:\Temp\RedmiWatch2SOFT\!WacthFaces\input\%file%_packed"
echo.
pause

:Continue
IF "%1"=="" echo No bin file given. Usage: %~nx0 path\to\file.bin

