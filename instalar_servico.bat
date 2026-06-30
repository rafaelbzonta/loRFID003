@echo off
:: ============================================================
::  loRFID003  —  instalar_servico.bat
::  Desenvolvido por Rafael Zonta
::  - Adiciona IPs de loopback para cada leitor
::  - Instala o bridge como Serviço do Windows
::  Clique direito > Executar como administrador
:: ============================================================
title Instalar loRFID003

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause & exit /b 1
)

cd /d "%~dp0"

echo ============================================================
echo   loRFID003  —  Desenvolvido por Rafael Zonta
echo ============================================================
echo.

:: ── 1. Dependencias ─────────────────────────────────────────
echo [1/5] Instalando dependencia pywin32...
pip install pywin32 --quiet
if %errorlevel% neq 0 ( echo [ERRO] Falha pywin32. & pause & exit /b 1 )

:: ── 2. Coletar local_ips do config.py ───────────────────────
echo [2/5] Lendo leitores do config.py...
python -c "import config; [print(r['local_ip']) for r in config.READERS]" > "%TEMP%\local_ips.txt" 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ler config.py. Verifique o arquivo.
    pause & exit /b 1
)

:: ── 3. Adicionar IPs de loopback (pula 127.0.0.1 que ja existe) ──
echo [3/5] Configurando IPs de loopback...
for /f "usebackq tokens=*" %%I in ("%TEMP%\local_ips.txt") do (
    if not "%%I"=="127.0.0.1" (
        :: Remove se ja existir para evitar duplicata
        netsh interface ipv4 delete address "Loopback Pseudo-Interface 1" %%I >nul 2>&1
        netsh interface ipv4 add address "Loopback Pseudo-Interface 1" %%I 255.0.0.0
        if %errorlevel%==0 (
            echo   + Loopback adicionado: %%I
        ) else (
            echo   ! Falha ao adicionar %%I — verifique se o adaptador loopback existe.
        )
    ) else (
        echo   + 127.0.0.1 ja existe ^(padrao^)
    )
)

:: ── 4. Firewall ──────────────────────────────────────────────
echo [4/5] Configurando Firewall...
netsh advfirewall firewall delete rule name="N5PROX Bridge UDP" >nul 2>&1
netsh advfirewall firewall add rule name="N5PROX Bridge UDP" dir=in action=allow protocol=UDP localport=14445 >nul
echo   + UDP 14445 liberado
python -c "import config; print(config.TCP_PORT)" > "%TEMP%\tcp_port.txt" 2>nul
set /p TCP_PORT= < "%TEMP%\tcp_port.txt"
netsh advfirewall firewall delete rule name="N5PROX Bridge TCP" >nul 2>&1
netsh advfirewall firewall add rule name="N5PROX Bridge TCP" dir=in action=allow protocol=TCP localport=%TCP_PORT% >nul
echo   + TCP %TCP_PORT% liberado

:: ── 5. Instalar servico ──────────────────────────────────────
echo [5/5] Instalando servico Windows...
sc stop N5ProxBridge >nul 2>&1
sc delete N5ProxBridge >nul 2>&1
timeout /t 2 >nul

python n5prox_service.py install
if %errorlevel% neq 0 ( echo [ERRO] Falha ao instalar servico. & pause & exit /b 1 )

sc config N5ProxBridge start= auto
sc start N5ProxBridge

echo.
echo ============================================================
echo  Instalacao concluida!
echo.
echo  No PaperCut, configure cada dispositivo com:
echo    Modo de Conexao : Generico
echo    Porta de rede   : %TCP_PORT%
echo    Hostname / IP   : (o local_ip de cada leitor no config.py)
echo.
echo  Gerenciar servico:
echo    sc query  N5ProxBridge
echo    sc stop   N5ProxBridge
echo    sc start  N5ProxBridge
echo    sc delete N5ProxBridge
echo.
echo  Log: %~dp0n5prox_bridge.log
echo ============================================================
pause
