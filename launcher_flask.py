# ============================================================
# Launcher — Servidor Flask (app.py)
# Desenvolvido por Íkaro Henrique & Matheus Kioshi
# ============================================================

import tkinter as tk
import subprocess, threading, sys, os, re, webbrowser, shutil

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
APP_PY       = os.path.join(LAUNCHER_DIR, "app.py")


def ler_config_web():
    """L apenas HOST/PORT do .env externo; valores invalidos sao descartados."""
    host, porta = "127.0.0.1", "5000"
    try:
        with open(os.path.join(LAUNCHER_DIR, ".env"), encoding="utf-8") as fh:
            for raw in fh:
                linha = raw.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, valor = (parte.strip() for parte in linha.split("=", 1))
                valor = valor.strip("'\"")
                if chave == "HOST" and re.fullmatch(r"[A-Za-z0-9._:\[\]]{1,60}", valor):
                    host = valor
                elif chave == "PORT" and valor.isdigit() and 1 <= int(valor) <= 65535:
                    porta = str(int(valor))
    except OSError:
        pass
    exibicao = "127.0.0.1" if host in ("0.0.0.0", "::", "[::]") else host
    if ":" in exibicao and not exibicao.startswith("["):
        exibicao = "[" + exibicao + "]"
    return exibicao, porta


HOST_EXIBICAO, PORTA = ler_config_web()
URL_DASHBOARD = f"http://{HOST_EXIBICAO}:{PORTA}"


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


def encontrar_python():
    """
    Busca o executável real do Python — nunca retorna o próprio .exe do launcher.
    """
    candidatos = [
        # Python no PATH do sistema
        shutil.which("python"),
        shutil.which("python3"),
        # Locais comuns no Windows
        r"C:\Python313\python.exe",
        r"C:\Python312\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python39\python.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python313\python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python312\python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python311\python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe"),
        os.path.expandvars(r"%APPDATA%\Python\Python313\python.exe"),
    ]
    for c in candidatos:
        if c and os.path.isfile(c):
            # Garante que não é o próprio launcher
            if "launcher" not in c.lower() and c.endswith(".exe") or c.endswith("python") or c.endswith("python3"):
                return c
    return None


PYTHON_EXE = encontrar_python()

processo = None
rodando  = False


def toggle():
    if not rodando:
        iniciar()
    else:
        parar()


def iniciar():
    global processo, rodando
    if not PYTHON_EXE:
        log("ERRO: Python nao encontrado no sistema.")
        log("Instale Python em https://python.org e reinicie.")
        return
    if not os.path.exists(APP_PY):
        log(f"ERRO: app.py nao encontrado em: {APP_PY}")
        return
    try:
        processo = subprocess.Popen(
            [PYTHON_EXE, APP_PY],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=LAUNCHER_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        rodando = True
        atualizar_ui()
        log(f"Servidor iniciado com {PYTHON_EXE}")
        log(f"Acesse: {URL_DASHBOARD}")
        threading.Thread(target=ler_saida, daemon=True).start()
    except Exception as e:
        log(f"Erro ao iniciar: {e}")


def parar():
    global processo, rodando
    if processo:
        try:
            processo.terminate()
            processo.wait(timeout=5)
        except Exception:
            try: processo.kill()
            except Exception: pass
        processo = None
    rodando = False
    atualizar_ui()
    log("Servidor encerrado.")


def ler_saida():
    try:
        for linha in processo.stdout:
            log(linha.rstrip())
    except Exception:
        pass
    if rodando:
        root.after(0, parar)


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
            lbl_status.configure(text="  Rodando", fg=GREEN)
            btn_toggle.configure(text="   Desligar   ", bg=RED,
                                 activebackground=RED2, fg=TEXT,
                                 activeforeground=TEXT)
            btn_browser.configure(state="normal", cursor="hand2", fg=TEXT)
        else:
            lbl_status.configure(text="  Parado", fg=MUTED)
            btn_toggle.configure(text="   Ligar   ", bg=GREEN,
                                 activebackground=GREEN2, fg="#000",
                                 activeforeground="#000")
            btn_browser.configure(state="disabled", cursor="arrow", fg=MUTED)
    root.after(0, _f)


def abrir_browser():
    webbrowser.open(URL_DASHBOARD)


def ao_fechar():
    parar()
    root.destroy()


# ── Janela ───────────────────────────────────────────────────
root = tk.Tk()
root.title("Rastreio WA — Servidor Flask")
root.geometry("660x520")
root.resizable(False, False)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", ao_fechar)

# Header
header = tk.Frame(root, bg=BG2, height=70)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="📦", font=("Segoe UI", 26),
         bg=BG2, fg=TEXT).pack(side="left", padx=(20, 10))
hinfo = tk.Frame(header, bg=BG2)
hinfo.pack(side="left", pady=12)
tk.Label(hinfo, text="Rastreio WA — Flask",
         font=("Segoe UI", 13, "bold"), bg=BG2, fg=TEXT).pack(anchor="w")
tk.Label(hinfo, text="SERVIDOR WEB + DASHBOARD",
         font=("Segoe UI", 8), bg=BG2, fg=MUTED).pack(anchor="w")

lbl_status = tk.Label(header, text="  Parado",
                       font=("Segoe UI", 10, "bold"), bg=BG2, fg=MUTED)
lbl_status.pack(side="right", padx=24)

tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

# Controles
ctrl = tk.Frame(root, bg=BG, pady=24, padx=28)
ctrl.pack(fill="x")

btn_toggle = tk.Button(
    ctrl, text="   Ligar   ",
    font=("Segoe UI", 11, "bold"),
    bg=GREEN, fg="#000000",
    activebackground=GREEN2, activeforeground="#000000",
    relief="flat", bd=0, cursor="hand2",
    padx=24, pady=12,
    command=toggle,
)
btn_toggle.pack(side="left")

btn_browser = tk.Button(
    ctrl, text="  Abrir Dashboard  ",
    font=("Segoe UI", 10, "bold"),
    bg=BG3, fg=MUTED,
    activebackground=BORDER, activeforeground=TEXT,
    relief="flat", bd=0, cursor="arrow",
    padx=20, pady=12,
    state="disabled",
    command=abrir_browser,
)
btn_browser.pack(side="left", padx=(14, 0))

# Info
py_info = PYTHON_EXE if PYTHON_EXE else "Python NAO encontrado"
tk.Label(root, text=f"  Python: {py_info}",
         font=("Segoe UI", 8), bg=BG,
         fg=MUTED if PYTHON_EXE else RED, anchor="w").pack(fill="x", padx=28, pady=(0, 2))
tk.Label(root, text=f"  app.py: {APP_PY}",
         font=("Segoe UI", 8), bg=BG, fg=MUTED,
         anchor="w").pack(fill="x", padx=28, pady=(0, 10))

tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

# Log
tk.Label(root, text="  LOG",
         font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED,
         anchor="w").pack(fill="x", padx=28, pady=(10, 4))

frame_log = tk.Frame(root, bg=BG3,
                     highlightbackground=BORDER, highlightthickness=1)
frame_log.pack(fill="both", expand=True, padx=28, pady=(0, 24))

txt = tk.Text(frame_log, bg=BG3, fg=TEXT,
              font=("Consolas", 9), relief="flat", bd=0,
              state="disabled", wrap="word", padx=12, pady=10)
txt.pack(side="left", fill="both", expand=True)

sb = tk.Scrollbar(frame_log, command=txt.yview,
                  bg=BG2, troughcolor=BG3, width=8)
sb.pack(side="right", fill="y")
txt.configure(yscrollcommand=sb.set)

if not PYTHON_EXE:
    log("AVISO: Python nao encontrado.")
    log("Instale em https://python.org e reinicie este launcher.")
else:
    log(f"Python encontrado: {PYTHON_EXE}")
    log("Aguardando — clique em Ligar para iniciar o servidor.")

root.mainloop()