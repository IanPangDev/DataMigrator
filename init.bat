@echo off
setlocal

echo ========================================
echo   Iniciando los Docker Compose indicados
echo ========================================
echo.

set folders=containers\hive containers\sql_server containers\oracle

for %%d in (%folders%) do (
    echo Ejecutando en %%d ...
    pushd %%d
    docker compose up --build -d
    if %errorlevel% neq 0 (
        echo Error ejecutando docker compose en %%d
    )
    popd
    echo.
)

echo ========================================
echo   Todos los servicios han sido levantados
echo ========================================
pause