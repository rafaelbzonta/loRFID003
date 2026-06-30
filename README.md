# loRFID003

Bridge N5PROX → PaperCut MF — Multi-Leitor, mesma porta TCP.

Converte pacotes UDP dos leitores N5PROX para TCP compatível com o PaperCut MF em modo **Fast Release (Network Card Reader)**.

Todos os leitores usam a **mesma porta TCP** — o PaperCut diferencia cada leitor pelo **IP de loopback**.

---

## Arquitetura

```
[N5PROX-1  192.168.254.97] ──┐
[N5PROX-2  192.168.254.98] ──┤── UDP:14445 ──► Bridge
[N5PROX-3  192.168.254.99] ──┘
                                      │
                           127.0.0.1:14443 ──► PaperCut Leitor-1
                           127.0.0.2:14443 ──► PaperCut Leitor-2
                           127.0.0.3:14443 ──► PaperCut Leitor-3
```

---

## Arquivos

| Arquivo                | Descrição                                      |
|------------------------|------------------------------------------------|
| `config.py`            |   **Configuração principal** — edite este      |
| `n5prox_bridge.py`     | Script principal do bridge                     |
| `n5prox_service.py`    | Wrapper para Serviço do Windows                |
| `iniciar_bridge.bat`   | Execução manual (testes)                       |
| `instalar_servico.bat` | Instala como serviço Windows (produção)        |
| `remover_servico.bat`  | Remove o serviço e IPs de loopback             |
| `n5prox_bridge.log`    | Log gerado automaticamente                     |

---

## Pré-requisitos

- **Python 3.10+** → https://www.python.org/downloads/
  - Marque "Add Python to PATH" na instalação
- **pywin32** (para serviço) → instalado automaticamente pelo bat

---

## 1. Configurar os leitores — `config.py`

```python
TCP_PORT = 14443   # Mesma porta para todos

READERS = [
    {
        "name"      : "Impressora-RH",
        "reader_ip" : "192.168.254.97",   # IP físico do N5PROX
        "local_ip"  : "127.0.0.1",        # IP loopback no PaperCut
    },
]
```

> Use sempre `127.0.0.X` para `local_ip` — o instalador adiciona os IPs
> extras no adaptador loopback do Windows automaticamente.

---

## 2. Configurar cada N5PROX

No software **Ethernet Reader Monitor UDP** de cada leitor:

| Campo          | Valor                                    |
|----------------|------------------------------------------|
| Server Address | IP do servidor PaperCut (ex: 192.168.254.247) |
| Server Port    | `14445`  ← UDP, igual para todos         |

Clicar em **Program** para gravar.

---

## 3. Configurar o PaperCut MF

Para **cada leitor**, crie um dispositivo com:

| Campo               | Valor                              |
|---------------------|------------------------------------|
| Tipo de Dispositivo | Fast Release (Network Card Reader) |
| Modo de Conexão     | **Genérico**                       |
| Porta de rede       | `14443`  ← igual para todos        |
| Hostname / IP       | o `local_ip` do leitor no config   |

Exemplo:

| Dispositivo PaperCut | Hostname  | Porta |
|----------------------|-----------|-------|
| Impressora-RH        | 127.0.0.1 | 14443 |
| Impressora-TI        | 127.0.0.2 | 14443 |
| Impressora-DP        | 127.0.0.3 | 14443 |

---

## 4. Testar (modo manual)

```
iniciar_bridge.bat  ←  clique direito > Executar como administrador
```

Log esperado:
```
[INFO] 3 leitor(es) configurado(s)  [TCP porta: 14443]
[INFO]  • Impressora-RH  | reader: 192.168.254.97 → local: 127.0.0.1:14443
[INFO]  • Impressora-TI  | reader: 192.168.254.98 → local: 127.0.0.2:14443
[INFO] Listener UDP ativo na porta 14445
[INFO] TCP aguardando PaperCut em 127.0.0.1:14443
[INFO] PaperCut conectado → Impressora-RH
[INFO] ✅ Cartão: 2067267076  ←  Impressora-RH (192.168.254.97)
[INFO] → PaperCut [Impressora-RH]: 2067267076
```

---

## 5. Produção — instalar como serviço

```
instalar_servico.bat  ←  clique direito > Executar como administrador
```

O serviço **N5ProxBridge** iniciará automaticamente com o Windows, já com os IPs de loopback configurados.

```
sc query N5ProxBridge   ← verificar status
sc stop  N5ProxBridge   ← parar
sc start N5ProxBridge   ← iniciar
```

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|---------------|---------|
| `UDP bind: 10013` | Sem permissão | Executar como Administrador |
| Pacotes UDP não chegam | IP errado no leitor | Conferir Server Address no Ethernet Reader Monitor |
| `bind error` no TCP | IP loopback não existe | Rodar `instalar_servico.bat` para criá-lo |
| PaperCut não conecta | Hostname/porta errados | Conferir `local_ip` e `TCP_PORT` no PaperCut |
| Cartão não liberado | Número errado no usuário | Copiar UID do log e cadastrar no PaperCut |
| Precisa ver pacotes brutos | Debug | Editar `config.py` → `LOG_LEVEL = "DEBUG"` |

### Desenvolvido por Rafael Zonta