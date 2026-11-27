# ============================================================
# Sistema de Rastreamento de Encomendas via WhatsApp
# Desenvolvido por:
#   Íkaro Henrique Marçal Alexandre
#   Matheus Kioshi Fernandes Numata
#
# © 2025 - Todos os direitos reservados.
# Este software é propriedade intelectual dos autores.
# A reprodução, modificação ou distribuição não autorizada
# é estritamente proibida.
# ============================================================

from __future__ import annotations

import functools
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
from flask import Flask, Response, jsonify, redirect, render_template, request, session


def load_env(path: str = ".env") -> None:
    """Carrega KEY=VALUE de .env sem sobrescrever variáveis já exportadas."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            os.environ.setdefault(key, value)


load_env()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY nao configurada. Defina no ambiente ou no arquivo .env.")

DADOS_FILE = os.getenv("DADOS_FILE", "dados.json")

app = Flask(__name__, static_folder="static")
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE=os.getenv("SESSION_COOKIE_SAMESITE", "Lax"),
    SESSION_COOKIE_SECURE=env_bool("COOKIE_SECURE"),
    MAX_CONTENT_LENGTH=16 * 1024,
)


# ---------------------------------------------------------------------------
# Transporte seguro: Basic Auth somente em loopback ou HTTPS/proxy confiável
# ---------------------------------------------------------------------------

def _is_loopback(address: str) -> bool:
    try:
        return ipaddress.ip_address(address).is_loopback
    except ValueError:
        return False


def _ips_proxy_confiaveis() -> set[str]:
    """Aceita apenas endereços IP válidos; entradas inválidas são ignoradas."""
    confiaveis: set[str] = set()
    for item in os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            confiaveis.add(str(ipaddress.ip_address(item)))
        except ValueError:
            continue
    return confiaveis


def transporte_seguro() -> bool:
    """Bloqueia credenciais Basic/Bearer enviadas em HTTP para redes externas."""
    remote = request.remote_addr or ""
    if _is_loopback(remote):
        return True
    if request.is_secure:
        return True
    if env_bool("TRUST_PROXY") and request.headers.get("X-Forwarded-Proto", "").lower() == "https":
        return remote in _ips_proxy_confiaveis()
    return False


def resposta_erro(status: int, mensagem: str) -> Response:
    return Response(mensagem, status=status, mimetype="text/plain; charset=utf-8")


def _hash_senha(senha: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    derivada = hashlib.scrypt(senha.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return "scrypt${}${}".format(salt.hex(), derivada.hex())


def _verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        algoritmo, salt_hex, hash_hex = armazenado.split("$", 2)
        if algoritmo != "scrypt":
            return False
        esperado = bytes.fromhex(hash_hex)
        calculado = hashlib.scrypt(
            senha.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1, dklen=len(esperado)
        )
        return hmac.compare_digest(calculado, esperado)
    except (ValueError, TypeError):
        return False


def dashboard_auth(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not transporte_seguro():
            return resposta_erro(403, "Acesso remoto exige HTTPS ou proxy confiável.")
        usuario = os.getenv("DASH_USER")
        senha_hash = os.getenv("DASH_PASSWORD_HASH")
        if not usuario or not senha_hash:
            return resposta_erro(503, "Autenticacao nao configurada.")
        auth = request.authorization
        if not auth or auth.type.lower() != "basic":
            return _resposta_basic()
        if not hmac.compare_digest(auth.username or "", usuario):
            return _resposta_basic()
        if not _verificar_senha(auth.password or "", senha_hash):
            return _resposta_basic()
        return view(*args, **kwargs)
    return wrapper


def _resposta_basic() -> Response:
    response = resposta_erro(401, "Credenciais invalidas.")
    response.headers["WWW-Authenticate"] = 'Basic realm="Rastreio", charset="UTF-8"'
    return response


def servico_auth(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not transporte_seguro():
            return resposta_erro(403, "Acesso remoto exige HTTPS ou proxy confiável.")
        token = os.getenv("DADOS_TOKEN")
        if not token:
            return resposta_erro(503, "Token de servico nao configurado.")
        cabecalho = request.headers.get("Authorization", "")
        partes = cabecalho.split(None, 1)
        if len(partes) != 2 or partes[0].lower() != "bearer":
            return resposta_erro(401, "Credenciais invalidas.")
        if not hmac.compare_digest(partes[1], token):
            return resposta_erro(401, "Credenciais invalidas.")
        return view(*args, **kwargs)
    return wrapper


def csrf_token() -> str:
    token = session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf"] = token
    return token


def csrf_valido() -> bool:
    esperado = session.get("csrf", "")
    enviado = request.form.get("csrf_token", "")
    return bool(esperado) and hmac.compare_digest(enviado, esperado)


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------

def carregar_dados() -> dict:
    if not os.path.exists(DADOS_FILE):
        return {}
    try:
        with open(DADOS_FILE, "r", encoding="utf-8") as fh:
            dados = json.load(fh)
        return dados if isinstance(dados, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def salvar_dados(dados: dict) -> None:
    temporario = DADOS_FILE + ".tmp"
    with open(temporario, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, indent=4, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(temporario, DADOS_FILE)
    try:
        os.chmod(DADOS_FILE, 0o600)
    except OSError:
        pass


def detectar_transportadora(codigo: str) -> dict:
    """Retorna {'label': '...', 'classe': '...'} para uso no template."""
    c = codigo.upper().strip()
    if re.match(r'^[A-Z]{2}\d{9}[A-Z]{2}$', c):
        return {"label": "Correios",   "classe": "carrier-correios"}
    if re.match(r'^(JD)?\d{10,14}$', c):
        return {"label": "Jadlog",     "classe": "carrier-jadlog"}
    if re.match(r'^(TE|TX)\d+$', c):
        return {"label": "Total Exp.", "classe": "carrier-total"}
    if re.match(r'^(SEQ|SQ|BP|LG|AC)\d+$', c):
        return {"label": "Outros",     "classe": "carrier-outros"}
    return {"label": "Auto", "classe": "carrier-outros"}


def migrar_legado(dados: dict) -> dict:
    """Converte o formato antigo {"numero": "codigo"} para {"numero": ["codigo"]}."""
    for nome in list(dados):
        contatos = dados.get(nome)
        if not isinstance(contatos, dict):
            continue
        for numero, valor in contatos.items():
            if isinstance(valor, str):
                contatos[numero] = [valor]
    return dados


def campos_validos(nome: str, numero: str, codigo: str) -> bool:
    if not (1 <= len(nome) <= 80) or any(ord(char) < 32 or char in "<>" for char in nome):
        return False
    if not re.fullmatch(r"\+?\d{8,15}", numero):
        return False
    if not re.fullmatch(r"[A-Za-z0-9-]{4,40}", codigo):
        return False
    return True


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.after_request
def cabecalhos_seguranca(response: Response) -> Response:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    )
    return response


@app.route("/")
@dashboard_auth
def index():
    dados = migrar_legado(carregar_dados())

    dados_enriquecidos = {}
    for nome, contatos in dados.items():
        if not isinstance(contatos, dict):
            continue
        dados_enriquecidos[nome] = {}
        for numero, codigos in contatos.items():
            lista = codigos if isinstance(codigos, list) else [codigos]
            dados_enriquecidos[nome][numero] = [
                {"codigo": cod, "transportadora": detectar_transportadora(str(cod))}
                for cod in lista
            ]

    return render_template("index.html", dados=dados_enriquecidos, csrf_token=csrf_token())


@app.route("/adicionar", methods=["POST"])
@dashboard_auth
def adicionar():
    if not csrf_valido():
        return resposta_erro(403, "Token CSRF invalido.")

    nome = (request.form.get("nome") or "").strip()
    numero = (request.form.get("numero") or "").strip()
    codigo = (request.form.get("codigo") or "").strip()

    if not campos_validos(nome, numero, codigo):
        return resposta_erro(400, "Dados invalidos.")

    dados = migrar_legado(carregar_dados())
    dados.setdefault(nome, {})
    dados[nome].setdefault(numero, [])
    if codigo not in dados[nome][numero]:
        dados[nome][numero].append(codigo)
        salvar_dados(dados)

    return redirect("/")


@app.route("/remover", methods=["POST"])
@dashboard_auth
def remover():
    if not csrf_valido():
        return resposta_erro(403, "Token CSRF invalido.")

    nome = (request.form.get("nome") or "").strip()
    numero = (request.form.get("numero") or "").strip()
    codigo = (request.form.get("codigo") or "").strip()

    if not campos_validos(nome, numero, codigo):
        return resposta_erro(400, "Dados invalidos.")

    dados = migrar_legado(carregar_dados())
    if nome in dados and numero in dados[nome]:
        lista = dados[nome][numero]
        if isinstance(lista, list) and codigo in lista:
            lista.remove(codigo)
        if not dados[nome][numero]:
            del dados[nome][numero]
        if not dados[nome]:
            del dados[nome]
        salvar_dados(dados)

    return redirect("/")


@app.route("/dados")
@servico_auth
def dados():
    return jsonify(migrar_legado(carregar_dados()))


@app.errorhandler(404)
def nao_encontrado(_error):
    return resposta_erro(404, "Nao encontrado.")


@app.errorhandler(405)
def metodo_nao_permitido(_error):
    return resposta_erro(405, "Metodo nao permitido.")


@app.errorhandler(413)
def payload_grande(_error):
    return resposta_erro(413, "Requisicao muito grande.")


@app.errorhandler(500)
def erro_interno(_error):
    return resposta_erro(500, "Erro interno.")


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
        use_reloader=False,
    )
