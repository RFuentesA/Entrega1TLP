@echo off
echo ========================================
echo BrickScript - Selector de Juegos
echo ========================================
echo.
echo Selecciona el juego que deseas jugar:
echo.
echo   1. Snake
echo   2. Tetris
echo.
set /p opcion="Ingresa tu opcion (1 o 2): "

if "%opcion%"=="1" (
    set juego=snake
) else if "%opcion%"=="2" (
    set juego=tetris
) else (
    echo.
    echo Error: Opcion invalida
    pause
    goto :eof
)

echo.
echo ========================================
echo BrickScript - Compilando y ejecutando
echo ========================================
echo.

REM Compilar el archivo .brik a .json
echo Compilando %juego%.brik...
python compiler.py ejemplos\%juego%.brik

if %errorlevel% neq 0 (
    echo.
    echo Error en la compilacion
    pause
    goto :eof
)

echo.
echo Ejecutando %juego%.json...
echo.
python runtime.py ejemplos\%juego%.json

pause
