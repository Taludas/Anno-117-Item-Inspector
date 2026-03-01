@echo off
setlocal enabledelayedexpansion

for /R %%F in (*_0.png) do (
    set "old=%%~fF"
    set "new=%%~dpF%%~nF"

    REM
    if "!new:~-2!"=="_0" (
        set "new=!new:~0,-2!.png"

        if exist "!new!" del /F /Q "!new!"
        move /Y "!old!" "!new!" >nul
    )
)

endlocal