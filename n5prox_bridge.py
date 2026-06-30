"""
=============================================================================
  loRFID003  —  n5prox_bridge.py
  Desenvolvido por Rafael Zonta
=============================================================================
  Arquitetura:

    [Leitor-1 192.168.254.97] ──┐
    [Leitor-2 192.168.254.98] ──┤── UDP:14445 ──► Bridge
    [Leitor-3 192.168.254.99] ──┘
                                         │
                              127.0.0.1:14443 ──► PaperCut (Leitor-1)
                              127.0.0.2:14443 ──► PaperCut (Leitor-2)
                              127.0.0.3:14443 ──► PaperCut (Leitor-3)

  - Um único listener UDP recebe todos os pacotes
  - Cada leitor é identificado pelo IP de origem do UDP
  - Cada leitor tem seu próprio IP de loopback (mesma porta TCP para todos)
=============================================================================
"""

import socket
import threading
import logging
import queue
import time
import sys
import os

import config

# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)-5s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("bridge")


# ─────────────────────────────────────────────
#  Estado global dos leitores
#  reader_state[reader_ip] = {
#      "config"    : { name, reader_ip, local_ip },
#      "queue"     : queue.Queue(),
#      "last_card" : str | None,
#      "last_ts"   : float,
#  }
# ─────────────────────────────────────────────
reader_state: dict = {}


def build_reader_state():
    for r in config.READERS:
        reader_state[r["reader_ip"]] = {
            "config"    : r,
            "queue"     : queue.Queue(),
            "last_card" : None,
            "last_ts"   : 0.0,
        }

    log.info(f"{len(reader_state)} leitor(es) configurado(s)  [TCP porta: {config.TCP_PORT}]:")
    for ip, s in reader_state.items():
        log.info(
            f"  • {s['config']['name']:15s} | "
            f"reader: {ip:18s} → "
            f"local: {s['config']['local_ip']}:{config.TCP_PORT}"
        )


# ─────────────────────────────────────────────
#  Parser do pacote UDP
#  Formato confirmado: "0x7b3b0e04,0x001a484c,012345\x00"
# ─────────────────────────────────────────────
def parse_card(data: bytes, addr: tuple) -> str | None:
    log.debug(f"UDP {addr[0]}:{addr[1]} | {len(data)}b | {data.hex()}")

    try:
        text = data.decode("ascii", errors="ignore").strip().rstrip("\x00").strip()
    except Exception as e:
        log.warning(f"Erro ao decodificar pacote de {addr[0]}: {e}")
        return None

    log.debug(f"  ASCII: {text}")
    parts = [p.strip() for p in text.split(",")]

    if not parts:
        return None

    uid_field = parts[0]

    # Formato "0xABCDEF01"
    if uid_field.lower().startswith("0x"):
        try:
            uid_int = int(uid_field, 16)
            uid_le  = int.from_bytes(uid_int.to_bytes(4, "big"), "little")
            log.debug(f"  UID big-endian : {uid_int}")
            log.debug(f"  UID lil-endian : {uid_le}")
            return str(uid_int)
        except (ValueError, OverflowError):
            log.warning(f"  Não foi possível converter '{uid_field}'")

    if uid_field.isdigit():
        return uid_field

    log.warning(f"  Formato inesperado: '{text}'")
    return None


# ─────────────────────────────────────────────
#  Thread: Listener UDP único
# ─────────────────────────────────────────────
def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", config.UDP_PORT))
    except OSError as e:
        log.error(f"Erro ao abrir UDP:{config.UDP_PORT} → {e}")
        log.error("Execute como Administrador ou libere a porta no Firewall.")
        sys.exit(1)

    log.info(f"Listener UDP ativo na porta {config.UDP_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
        except Exception as e:
            log.error(f"Erro UDP recvfrom: {e}")
            continue

        src_ip = addr[0]

        if src_ip not in reader_state:
            log.debug(f"Pacote de IP não cadastrado ignorado: {src_ip}")
            continue

        state = reader_state[src_ip]
        card_id = parse_card(data, addr)
        if not card_id:
            continue

        # Debounce
        now = time.time()
        if card_id == state["last_card"] and (now - state["last_ts"]) < config.DEBOUNCE_TIME:
            log.debug(f"  Debounce [{state['config']['name']}]: ignorando {card_id}")
            continue

        state["last_card"] = card_id
        state["last_ts"]   = now

        log.info(f"✅ Cartão: {card_id}  ←  {state['config']['name']} ({src_ip})")
        state["queue"].put(card_id)


# ─────────────────────────────────────────────
#  Thread: Servidor TCP por leitor (mesmo porto, IP diferente)
# ─────────────────────────────────────────────
def handle_papercut_client(conn: socket.socket, addr: tuple, state: dict):
    name   = state["config"]["name"]
    card_q = state["queue"]
    log.info(f"PaperCut conectado → {name}  (de {addr[0]}:{addr[1]})")

    try:
        while True:
            try:
                card_id = card_q.get(timeout=5)
            except queue.Empty:
                try:
                    conn.sendall(b"\n")
                except Exception:
                    log.warning(f"[{name}] PaperCut desconectou.")
                    break
                continue

            payload = f"{card_id}\n".encode("ascii")
            try:
                conn.sendall(payload)
                log.info(f"→ PaperCut [{name}]: {card_id}")
            except Exception as e:
                log.error(f"[{name}] Erro ao enviar: {e}")
                card_q.put(card_id)
                break
    finally:
        conn.close()
        log.info(f"[{name}] Conexão encerrada.")


def tcp_server_for_reader(state: dict):
    """Servidor TCP em local_ip:TCP_PORT dedicado a um leitor."""
    name     = state["config"]["name"]
    local_ip = state["config"]["local_ip"]
    port     = config.TCP_PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((local_ip, port))
    except OSError as e:
        log.error(f"[{name}] Erro ao bind em {local_ip}:{port} → {e}")
        log.error(f"[{name}] Verifique se o IP {local_ip} está ativo no adaptador loopback.")
        return

    server.listen(1)
    log.info(f"[{name}] TCP aguardando PaperCut em {local_ip}:{port}")

    while True:
        try:
            conn, addr = server.accept()
            t = threading.Thread(
                target=handle_papercut_client,
                args=(conn, addr, state),
                daemon=True,
                name=f"TCP-{name}",
            )
            t.start()
        except Exception as e:
            log.error(f"[{name}] Erro no accept: {e}")
            time.sleep(1)


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("  loRFID003  —  Desenvolvido por Rafael Zonta")
    log.info("=" * 60)

    build_reader_state()

    for state in reader_state.values():
        t = threading.Thread(
            target=tcp_server_for_reader,
            args=(state,),
            daemon=True,
            name=f"TCP-{state['config']['name']}",
        )
        t.start()

    # Listener UDP único — bloqueia aqui
    udp_listener()


if __name__ == "__main__":
    main()
