"""
=============================================================================
  loRFID003 —  n5prox_service.py
  Desenvolvido por Rafael Zonta
  Wrapper para Serviço do Windows
  Requer : pip install pywin32
  Instalar: python n5prox_service.py install
  Iniciar : sc start N5ProxBridge
=============================================================================
"""

import sys
import os
import threading
import servicemanager
import win32event
import win32service
import win32serviceutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n5prox_bridge import build_reader_state, reader_state, tcp_server_for_reader, udp_listener, log
import config


class N5ProxBridgeService(win32serviceutil.ServiceFramework):
    _svc_name_         = "N5ProxBridge"
    _svc_display_name_ = "loRFID003 — N5PROX → PaperCut Bridge"
    _svc_description_  = (
        "loRFID003 | Desenvolvido por Rafael Zonta. "
        "Converte pacotes UDP dos leitores N5PROX para TCP compatível com "
        "PaperCut MF Fast Release. Multi-leitor via IPs de loopback."
    )

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        log.info("Serviço parando...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        log.info("Serviço loRFID003 iniciado — Desenvolvido por Rafael Zonta.")

        build_reader_state()

        for state in reader_state.values():
            t = threading.Thread(
                target=tcp_server_for_reader,
                args=(state,),
                daemon=True,
                name=f"TCP-{state['config']['name']}",
            )
            t.start()

        t_udp = threading.Thread(target=udp_listener, daemon=True, name="UDP-Listener")
        t_udp.start()

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        log.info("Serviço N5ProxBridge encerrado.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(N5ProxBridgeService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(N5ProxBridgeService)
