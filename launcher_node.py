# ============================================================
# Launcher — Bot WhatsApp Node.js (whatsapp-rastreio.js)
# Desenvolvido por Íkaro Henrique & Matheus Kioshi
# ============================================================

import tkinter as tk
import subprocess, threading, sys, os, re, shutil

BG     = "#0d0f12"
BG2    = "#13161b"
BG3    = "#1a1e26"
BORDER = "#1f2530"
GREEN  = "#25d366"
GREEN2 = "#1a9e4a"
RED    = "#f87171"
RED2   = "#c0392b"
TEXT   = "#e8eaf0"
MUTED  = "#6b7280"

LAUNCHER_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
BOT_JS       = os.path.join(LAUNCHER_DIR, "whatsapp-rastreio.js")
QR_PNG        = os.path.join(LAUNCHER_DIR, "qr_temp.png")
WA_SIGNAL     = os.path.join(LAUNCHER_DIR, "wa_connected.signal")


def valores_sensiveis():
    """Carrega valores do .env apenas para removê-los de qualquer log."""
    chaves = {"SECRET_KEY", "DASH_USER", "DASH_PASSWORD_HASH", "DADOS_TOKEN", "TRACKING_API_KEY"}
    valores = []
    try:
        with open(os.path.join(LAUNCHER_DIR, ".env"), encoding="utf-8") as fh:
            for raw in fh:
                linha = raw.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, valor = (parte.strip() for parte in linha.split("=", 1))
                valor = valor.strip("'\"")
                if chave.upper() in chaves and len(valor) >= 4:
                    valores.append(valor)
    except OSError:
        pass
    return valores


SEGREDOS_LOG = valores_sensiveis()


def sanitizar_log(msg):
    texto = str(msg)
    for valor in SEGREDOS_LOG:
        texto = texto.replace(valor, "[REDACTED]")
    texto = re.sub(r"(?i)(authorization\s*[:=]\s*)(apikey|bearer)\s+\S+", r"\1\2 [REDACTED]", texto)
    texto = re.sub(r"(?i)(api[_-]?key|token|secret|password|senha)\s*[:=]\s*\S+", r"\1=[REDACTED]", texto)
    texto = re.sub(r"(?<!\d)\+?\d{10,13}(?!\d)", "[TELEFONE_REDACTED]", texto)
    return re.sub(r"[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL_REDACTED]", texto)


def encontrar_node():
    node = shutil.which("node")
    if node:
        return node
    for c in [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files\nodejs\node.EXE",
        os.path.expandvars(r"%APPDATA%\nvm\current\node.exe"),
        os.path.expandvars(r"%NVM_SYMLINK%\node.exe"),
    ]:
        if os.path.isfile(c):
            return c
    return None

NODE_EXE = encontrar_node()
processo = None
rodando  = False
qr_photo = None  # mantém referência — evita garbage collection


def toggle():
    if not rodando:
        iniciar()
    else:
        parar()


def iniciar():
    global processo, rodando
    if not NODE_EXE:
        log("ERRO: Node.js nao encontrado. Instale em https://nodejs.org")
        return
    if not os.path.exists(BOT_JS):
        log(f"ERRO: whatsapp-rastreio.js nao encontrado em:\n  {BOT_JS}")
        return
    if os.path.exists(QR_PNG):
        try: os.remove(QR_PNG)
        except: pass

    try:
        # Limpa sinais antigos
        for f in [QR_PNG, WA_SIGNAL]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

        processo = subprocess.Popen(
            [NODE_EXE, BOT_JS],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=LAUNCHER_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        rodando = True
        atualizar_ui()
        log("Bot iniciado. Aguarde o QR Code...")
        threading.Thread(target=ler_saida, daemon=True).start()
        root.after(1000, verificar_qr)
        root.after(1000, monitorar_conexao)
    except Exception as e:
        log(f"Erro ao iniciar: {e}")


def parar():
    global processo, rodando
    if processo:
        try:
            processo.terminate()
            processo.wait(timeout=5)
        except:
            try: processo.kill()
            except: pass
        processo = None
    rodando = False
    atualizar_ui()
    esconder_qr()
    log("Bot encerrado.")


def ler_saida():
    """Lê stdout linha a linha — apenas para log visual."""
    try:
        for linha in iter(processo.stdout.readline, b""):
            try:
                linha = linha.decode("utf-8", errors="replace").rstrip()
            except Exception:
                continue
            if "QR_IMAGE_READY:" in linha:
                root.after(300, verificar_qr)
                continue
            if linha:
                log(linha)
    except Exception:
        pass
    if rodando:
        root.after(0, parar)


def verificar_qr():
    """Tenta carregar o PNG — repete até conseguir ou bot parar."""
    if os.path.exists(QR_PNG) and os.path.getsize(QR_PNG) > 0:
        root.after(0, carregar_qr_imagem)
    elif rodando:
        root.after(800, verificar_qr)


def carregar_qr_imagem():
    global qr_photo
    if not os.path.exists(QR_PNG):
        return
    try:
        qr_photo = tk.PhotoImage(file=QR_PNG)
        qr_label.configure(image=qr_photo)
        qr_hint.configure(text="📱 Escaneie o QR Code acima com o WhatsApp")
        # Redimensiona janela para acomodar o QR
        root.geometry("700x740")
    except Exception as e:
        log(f"Erro ao exibir QR: {e}")


def esconder_qr():
    global qr_photo
    qr_photo = None
    qr_label.configure(image="")
    qr_hint.configure(text="")
    root.geometry("700x580")


def monitorar_conexao():
    """Polling a cada 500ms — detecta wa_connected.signal no disco."""
    if os.path.exists(WA_SIGNAL):
        esconder_qr()
        log("✅ WhatsApp conectado! Bot em execução.")
    elif rodando:
        root.after(500, monitorar_conexao)


def log(msg):
    texto = sanitizar_log(msg)
    def _f():
        txt.configure(state="normal")
        txt.insert("end", texto + "\n")
        txt.see("end")
        txt.configure(state="disabled")
    root.after(0, _f)


def atualizar_ui():
    def _f():
        if rodando:
            lbl_status.configure(text="Ativo", fg=GREEN)
            btn_toggle.configure(
                text="   Desativar   ", bg=RED,
                activebackground=RED2, fg=TEXT, activeforeground=TEXT)
        else:
            lbl_status.configure(text="Inativo", fg=MUTED)
            btn_toggle.configure(
                text="   Ativar   ", bg=GREEN,
                activebackground=GREEN2, fg="#000", activeforeground="#000")
    root.after(0, _f)


def ao_fechar():
    parar()
    root.destroy()


# ── Janela ───────────────────────────────────────────────────
root = tk.Tk()
root.title("Rastreio WA — Bot WhatsApp")
root.geometry("700x580")
root.resizable(False, False)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", ao_fechar)

# ── Header ────────────────────────────────────────────────────
header = tk.Frame(root, bg=BG2, height=70)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="🤖", font=("Segoe UI", 26),
         bg=BG2, fg=TEXT).pack(side="left", padx=(20, 10))
hinfo = tk.Frame(header, bg=BG2)
hinfo.pack(side="left", pady=12)
tk.Label(hinfo, text="Rastreio WA — Bot",
         font=("Segoe UI", 13, "bold"), bg=BG2, fg=TEXT).pack(anchor="w")
tk.Label(hinfo, text="BOT WHATSAPP + RASTREAMENTO AUTOMÁTICO",
         font=("Segoe UI", 9), bg=BG2, fg=MUTED).pack(anchor="w")

lbl_status = tk.Label(header, text="Inativo",
                       font=("Segoe UI", 11, "bold"), bg=BG2, fg=MUTED)
lbl_status.pack(side="right", padx=24)

tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

# ── Controles ─────────────────────────────────────────────────
ctrl = tk.Frame(root, bg=BG, pady=20, padx=28)
ctrl.pack(fill="x")

btn_toggle = tk.Button(
    ctrl, text="   Ativar   ",
    font=("Segoe UI", 12, "bold"),
    bg=GREEN, fg="#000000",
    activebackground=GREEN2, activeforeground="#000000",
    relief="flat", bd=0, cursor="hand2",
    padx=28, pady=13,
    command=toggle,
)
btn_toggle.pack(side="left")

node_info = NODE_EXE if NODE_EXE else "Node.js NAO encontrado"
tk.Label(root, text=f"  Node.js: {node_info}",
         font=("Segoe UI", 9), bg=BG,
         fg=MUTED if NODE_EXE else RED, anchor="w").pack(fill="x", padx=28, pady=(0, 2))
tk.Label(root, text=f"  Script:  {BOT_JS}",
         font=("Segoe UI", 9), bg=BG, fg=MUTED,
         anchor="w").pack(fill="x", padx=28, pady=(0, 8))

tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

# ── QR Code (sempre no layout, visível só quando tiver imagem) ─
qr_frame = tk.Frame(root, bg=BG)
qr_frame.pack(fill="x")

qr_label = tk.Label(qr_frame, bg=BG, image="")
qr_label.pack(pady=(12, 4))

qr_hint = tk.Label(qr_frame, text="",
                    font=("Segoe UI", 10, "bold"),
                    bg=BG, fg=GREEN)
qr_hint.pack(pady=(0, 10))

tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

# ── Log ───────────────────────────────────────────────────────
tk.Label(root, text="  LOG",
         font=("Segoe UI", 9, "bold"), bg=BG, fg=MUTED,
         anchor="w").pack(fill="x", padx=28, pady=(8, 4))

frame_log = tk.Frame(root, bg=BG3,
                     highlightbackground=BORDER, highlightthickness=1)
frame_log.pack(fill="both", expand=True, padx=28, pady=(0, 20))

txt = tk.Text(
    frame_log, bg=BG3, fg=TEXT,
    font=("Consolas", 10),
    relief="flat", bd=0,
    state="disabled",
    wrap="word",
    padx=12, pady=10,
)
txt.pack(side="left", fill="both", expand=True)

sb = tk.Scrollbar(frame_log, command=txt.yview,
                  bg=BG2, troughcolor=BG3, width=8)
sb.pack(side="right", fill="y")
txt.configure(yscrollcommand=sb.set)

if not NODE_EXE:
    log("AVISO: Node.js nao encontrado.")
    log("Instale em https://nodejs.org e reinicie.")
else:
    log(f"Node.js: {NODE_EXE}")
    log("Aguardando — clique em Ativar para iniciar o bot.")

root.mainloop()