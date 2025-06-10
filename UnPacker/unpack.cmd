@echo off
setlocal enabledelayedexpansion

for %%F in (*.cpk) do (
    echo Processing %%F...
    CriPakTools.exe "%%F" ALL
)

echo All files have been processed.
pause

rem https://github.com/esperknight/CriPakTools