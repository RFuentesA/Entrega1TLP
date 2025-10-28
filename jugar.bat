@echo off
if "%1"=="" (
    echo ========================================
    echo Error: Debe especificar un juego
    echo ========================================
    echo.
    echo Uso: jugar [nombre_juego]
    echo.
    echo Ejemplos:
    echo   jugar tetris
    echo   jugar snake
    echo.
    goto :eof
)

echo ========================================
echo BrickScript - Compilando y ejecutando
echo ========================================
echo.

REM Compilar el archivo .brik a .json
echo Compilando %1.brik...
python compiler.py ..\ejemplos\%1.brik

if %errorlevel% neq 0 (
    echo.
    echo Error en la compilacion
    pause
    goto :eof
)

echo.
echo Ejecutando %1.json...
echo.
python runtime.py ..\ejemplos\%1.json

pause
