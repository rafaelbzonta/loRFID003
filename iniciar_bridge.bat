@echo off
:: ============================================================
::  loRFID003  —  iniciar_bridge.bat
::  Desenvolvido por Rafael Zonta
::  Execução manual para testes
::  Clique direito > Executar como administrador
:: ============================================================
title loRFID003  [TESTE]

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause & exit /b 1
)

cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Instale em: https://www.python.org/downloads/
    pause & exit /b 1
)

echo ============================================================
echo   loRFID003  —  Desenvolvido por Rafael Zonta  [MODO TESTE]
echo ============================================================
echo.

:: Adiciona IPs de loopback necessários
echo Configurando IPs de loopback...
python -c "import config; [print(r['local_ip']) for r in config.READERS]" > "%TEMP%\local_ips.txt" 2>nul
for /f "usebackq tokens=*" %%I in ("%TEMP%\local_ips.txt") do (
    if not "%%I"=="127.0.0.1" (
        netsh interface ipv4 delete address "Loopback Pseudo-Interface 1" %%I >nul 2>&1
        netsh interface ipv4 add address "Loopback Pseudo-Interface 1" %%I 255.0.0.0 >nul 2>&1
        echo   + Loopback: %%I
    )
)

:: Libera portas no firewall
echo Configurando Firewall...
netsh advfirewall firewall delete rule name="N5PROX Bridge UDP" >nul 2>&1
netsh advfirewall firewall add rule name="N5PROX Bridge UDP" dir=in action=allow protocol=UDP localport=14445 >nul
python -c "import config; print(config.TCP_PORT)" > "%TEMP%\tcp_port.txt" 2>nul
set /p TCP_PORT= < "%TEMP%\tcp_port.txt"
netsh advfirewall firewall delete rule name="N5PROX Bridge TCP" >nul 2>&1
netsh advfirewall firewall add rule name="N5PROX Bridge TCP" dir=in action=allow protocol=TCP localport=%TCP_PORT% >nul
echo   + UDP 14445 e TCP %TCP_PORT% liberados

echo.
echo Pressione CTRL+C para encerrar.
echo ============================================================
echo.

python n5prox_bridge.py
pause
