@echo off
:: ============================================================
::  loRFID003  —  remover_servico.bat
::  Desenvolvido por Rafael Zonta
::  Remove o serviço e os IPs de loopback adicionados
::  Clique direito > Executar como administrador
:: ============================================================
title Remover loRFID003

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause & exit /b 1
)

cd /d "%~dp0"

echo Parando e removendo servico...
sc stop N5ProxBridge >nul 2>&1
timeout /t 2 >nul
sc delete N5ProxBridge
python n5prox_service.py remove >nul 2>&1

echo Removendo IPs de loopback extras...
python -c "import config; [print(r['local_ip']) for r in config.READERS]" > "%TEMP%\local_ips.txt" 2>nul
for /f "usebackq tokens=*" %%I in ("%TEMP%\local_ips.txt") do (
    if not "%%I"=="127.0.0.1" (
        netsh interface ipv4 delete address "Loopback Pseudo-Interface 1" %%I >nul 2>&1
        echo   - Loopback removido: %%I
    )
)

echo Removendo regras de Firewall...
netsh advfirewall firewall delete rule name="N5PROX Bridge UDP" >nul 2>&1
netsh advfirewall firewall delete rule name="N5PROX Bridge TCP" >nul 2>&1
echo   - Regras removidas.

echo.
echo Remocao concluida.
pause
