# =============================================================================
#  loRFID003  —  config.py
#  Desenvolvido por Rafael Zonta
# =============================================================================
#  Todos os leitores usam a mesma porta TCP. O PaperCut diferencia os leitores pelo IP de loopback.
# =============================================================================

# ── Porta UDP (todos os leitores enviam para cá) ──────────────────────────────
UDP_PORT = 14445

# ── Porta TCP (igual para todos os leitores) ──────────────────────────────────
TCP_PORT = 14443

# ── Leitores ──────────────────────────────────────────────────────────────────
#
#  name        → nome(aparece no log)
#  reader_ip   → IP físico do leitor N5PROX (quem envia UDP)
#  local_ip    → IP de loopback que o bridge escuta (use 127.0.0.X)
#                Adicionado automaticamente pelo instalar_servico.bat
# ─────────────────────────────────────────────────────────────────────────────
READERS = [
    # {
    #    "name"      : "Leitor-01",
    #    "reader_ip" : "192.168.254.97",
    #    "local_ip"  : "127.0.0.1",
    # },
    # {
    #     "name"      : "Leitor-02",
    #     "reader_ip" : "192.168.254.98",
    #     "local_ip"  : "127.0.0.2",
    # },
    # {
    #     "name"      : "Leitor-03",
    #     "reader_ip" : "192.168.254.99",
    #     "local_ip"  : "127.0.0.3",
    # },
    # {
    #     "name"      : "Leitor-04",
    #     "reader_ip" : "192.168.254.100",
    #     "local_ip"  : "127.0.0.4",
    # },
    # {
    #     "name"      : "Leitor-05",
    #     "reader_ip" : "192.168.254.101",
    #     "local_ip"  : "127.0.0.5",
    # },
    # {
    #     "name"      : "Leitor-06",
    #     "reader_ip" : "192.168.254.102",
    #     "local_ip"  : "127.0.0.6",
    # },
    # {
    #     "name"      : "Leitor-07",
    #     "reader_ip" : "192.168.254.103",
    #     "local_ip"  : "127.0.0.7",
    # },
    # {
    #     "name"      : "Leitor-08",
    #     "reader_ip" : "192.168.254.104",
    #     "local_ip"  : "127.0.0.8",
    # },
    # {
    #     "name"      : "Leitor-09",
    #     "reader_ip" : "192.168.254.105",
    #     "local_ip"  : "127.0.0.9",
    # },
    # {
    #     "name"      : "Leitor-10",
    #     "reader_ip" : "192.168.254.106",
    #     "local_ip"  : "127.0.0.10",
    # },
    # {
    #     "name"      : "Leitor-11",
    #     "reader_ip" : "192.168.254.107",
    #     "local_ip"  : "127.0.0.11",
    # },
    # {
    #     "name"      : "Leitor-12",
    #     "reader_ip" : "192.168.254.108",
    #     "local_ip"  : "127.0.0.12",
    # },
    # {
    #     "name"      : "Leitor-13",
    #     "reader_ip" : "192.168.254.109",
    #     "local_ip"  : "127.0.0.13",
    # },
    # {
    #     "name"      : "Leitor-14",
    #     "reader_ip" : "192.168.254.110",
    #     "local_ip"  : "127.0.0.14",
    # },
    # {
    #     "name"      : "Leitor-15",
    #     "reader_ip" : "192.168.254.111",
    #     "local_ip"  : "127.0.0.15",
    # },
]

# ── Comportamento ─────────────────────────────────────────────────────────────
DEBOUNCE_TIME = 2.0     # Segundos entre leituras do mesmo cartão
LOG_FILE      = "n5prox_bridge.log"
LOG_LEVEL     = "INFO"  # "DEBUG" para ver pacotes brutos | "INFO" para produção
