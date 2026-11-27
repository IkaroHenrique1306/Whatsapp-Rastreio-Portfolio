// ============================================================
// Sistema de Rastreamento de Encomendas via WhatsApp
// Desenvolvido por:
//   Íkaro Henrique Marçal Alexandre
//   Matheus Kioshi Fernandes Numata
// ============================================================

const { Client, LocalAuth } = require("whatsapp-web.js");
const QRCodeImage = require("qrcode");
const axios       = require("axios");
const crypto      = require("crypto");
const path        = require("path");
const fs          = require("fs");

function loadEnv() {
    const arquivo = path.join(__dirname, ".env");
    if (!fs.existsSync(arquivo)) return;
    for (const linha of fs.readFileSync(arquivo, "utf8").split(/\r?\n/)) {
        const texto = linha.trim();
        if (!texto || texto.startsWith("#") || !texto.includes("=")) continue;
        const indice = texto.indexOf("=");
        let chave = texto.slice(0, indice).trim();
        let valor = texto.slice(indice + 1).trim();
        if (valor.length >= 2 && (valor.startsWith("'") && valor.endsWith("'") || valor.startsWith('"') && valor.endsWith('"'))) {
            valor = valor.slice(1, -1);
        }
        if (chave && process.env[chave] === undefined) process.env[chave] = valor;
    }
}
loadEnv();

// ======================== CONFIG ========================
const DADOS_URL_RAW = process.env.DADOS_URL || "http://127.0.0.1:5000/dados";
const DADOS_TOKEN = process.env.DADOS_TOKEN;
if (!DADOS_TOKEN) {
    console.error("Configuracao ausente: DADOS_TOKEN. Nenhuma requisicao foi enviada.");
    process.exit(1);
}

const DRY_RUN = true;
const MOCK_STATUS = process.env.TRACKING_MOCK_STATUS || (DRY_RUN ? "Status simulado (mock)" : "");
const MOCK_DADOS = process.env.DADOS_MOCK_FILE || "";
const INTERVALO = 60_000;
const QR_PATH = path.join(__dirname, "qr_temp.png");
const SIGNAL = path.join(__dirname, "wa_connected.signal");
const SESSION_PATH = process.env.WA_SESSION_PATH || "./whatsapp_session";
// ========================================================

function ehLoopback(host) {
    const h = normalizarHost(host);
    return h === "localhost" || h === "127.0.0.1" || h === "::1";
}

function normalizarHost(host) {
    return String(host).toLowerCase().replace(/^\[/, "").replace(/\]$/, "");
}

function hostsPermitidos(raw, nome) {
    const lista = String(raw).split(",").map(h => h.trim().toLowerCase()).filter(Boolean).map(normalizarHost);
    for (const h of lista) {
        if (h === "::1") continue;
        if (!/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/.test(h) || h.includes("*") || h.includes("/")) {
            console.error(`Whitelist invalida em ${nome}. Nenhuma credencial foi enviada.`);
            process.exit(1);
        }
    }
    return lista;
}

function validarUrlDestino(raw, permitidos, nome) {
    let url;
    try {
        url = new URL(raw);
    } catch (_) {
        console.error(`Configuracao invalida: ${nome}. Nenhuma requisicao foi enviada.`);
        process.exit(1);
    }
    const host = normalizarHost(url.hostname);
    if (!permitidos.includes(host)) {
        console.error(`Destino nao permitido para ${nome}. Nenhuma credencial foi enviada.`);
        process.exit(1);
    }
    if (url.protocol !== "https:" && !(nome === "DADOS_URL" && ehLoopback(host))) {
        console.error(`Protocolo nao permitido para ${nome}. Nenhuma credencial foi enviada.`);
        process.exit(1);
    }
    if (url.username || url.password) {
        console.error(`Credenciais na URL nao permitidas em ${nome}.`);
        process.exit(1);
    }
    if (url.port && url.port !== "443" && !(nome === "DADOS_URL" && ehLoopback(host))) {
        console.error(`Porta nao permitida para ${nome}.`);
        process.exit(1);
    }
    return url;
}

const DADOS_URL = validarUrlDestino(
    DADOS_URL_RAW,
    hostsPermitidos(process.env.DADOS_ALLOWED_HOSTS || "localhost,127.0.0.1,::1", "DADOS_ALLOWED_HOSTS"),
    "DADOS_URL"
);

function mascararNumero(numero) {
    const digitos = String(numero).replace(/\D/g, "");
    return digitos.length >= 2 ? `***${digitos.slice(-2)}` : "***";
}

function hash8(valor) {
    return crypto.createHash("sha256").update(String(valor)).digest("hex").slice(0, 8);
}

function tipoErro(erro) {
    return erro && erro.name ? erro.name : "Erro";
}

// Limpa sinais antigos somente no modo normal, para não alterar o estado local em DRY_RUN.
if (!DRY_RUN) {
    [QR_PATH, SIGNAL].forEach(f => { try { if (fs.existsSync(f)) fs.unlinkSync(f); } catch (e) {} });
}

const client = new Client({
    authTimeoutMs: 120000,
    authStrategy: new LocalAuth({ dataPath: SESSION_PATH }),
    puppeteer: {
    	headless: false,
    	executablePath: process.env.BROWSER_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
	timeout: 120000,
    	args: [
        	"--no-first-run",
		"--start-minimized",
    	],
    },
    webVersionCache: {
        type: "none",
    },
});

client.on("qr", async (qr) => {
    console.log("QR Code gerado. Escaneie com o WhatsApp pelo launcher.");
    try {
        await QRCodeImage.toFile(QR_PATH, qr, { width: 280, margin: 2 });
        console.log("QR_IMAGE_READY");
    } catch (e) {
        console.log("Erro ao gerar QR image: " + tipoErro(e));
    }
});

client.on("authenticated", () => {
    console.log("Autenticado. Finalizando conexao...");
    try { fs.writeFileSync(SIGNAL, "connected"); } catch (e) {}
});

client.on("ready", () => {
    console.log("WhatsApp pronto e conectado!");
    try { fs.writeFileSync(SIGNAL, "connected"); } catch (e) {}
    try { if (fs.existsSync(QR_PATH)) fs.unlinkSync(QR_PATH); } catch (e) {}
    if (!DRY_RUN) iniciarLoop();
});

client.on("auth_failure", () => {
    console.error("Falha na autenticacao do WhatsApp.");
    try { if (fs.existsSync(SIGNAL)) fs.unlinkSync(SIGNAL); } catch (e) {}
});

client.on("disconnected", () => {
    console.warn("Desconectado do WhatsApp. Reiniciando...");
    try { if (fs.existsSync(SIGNAL)) fs.unlinkSync(SIGNAL); } catch (e) {}
    setTimeout(() => client.initialize(), 5000);
});

// ===== Detecção de transportadora =====
function detectarTransportadora(codigo) {
    const c = codigo.toUpperCase().trim();
    if (/^[A-Z]{2}\d{9}[A-Z]{2}$/.test(c)) return "correios";
    if (/^(JD)?\d{10,14}$/.test(c))         return "jadlog";
    if (/^(TE|TX)\d+$/.test(c))             return "totalexpress";
    if (/^(SEQ|SQ|BP|LG|AC)\d+$/.test(c))  return "outros";
    return "tracking";
}

// ===== Rastreamento =====
async function obterStatusTracking(codigo) {
    return MOCK_STATUS || "Rastreamento simulado";
}

async function obterStatus(codigo) {
    const transportadora = detectarTransportadora(codigo);
    console.log(`Consultando codigo_hash=${hash8(codigo)} transportadora=${transportadora}`);
    return obterStatusTracking(codigo);
}

// ===== Loop principal =====
const ultimoStatus = {};

async function buscarDados() {
    if (DRY_RUN) {
        if (MOCK_DADOS && fs.existsSync(MOCK_DADOS)) {
            try {
                const conteudo = JSON.parse(fs.readFileSync(MOCK_DADOS, "utf8"));
                if (conteudo && typeof conteudo === "object") return conteudo;
            } catch (e) {
                console.warn(`Mock de dados invalido: ${tipoErro(e)}. Usando mock interno.`);
            }
        }
        return { "Destinatario_Teste": { "00000000000": ["MOCK00001"] } };
    }
    for (let i = 1; i <= 3; i++) {
        try {
            const res = await axios.get(DADOS_URL.toString(), {
                headers: { Authorization: `Bearer ${DADOS_TOKEN}` },
                timeout: 30_000,
                maxRedirects: 0,
            });
            return res.data;
        } catch (e) {
            console.warn(`Busca de dados tentativa ${i}/3 falhou: ${tipoErro(e)}`);
            if (i < 3) await new Promise(r => setTimeout(r, 5_000));
        }
    }
    return null;
}

async function verificarEEnviar() {
    const todosDados = await buscarDados();
    if (!todosDados) {
        console.error("Nao foi possivel buscar dados apos 3 tentativas.");
        return;
    }

    for (const [destinatarios, contatos] of Object.entries(todosDados)) {
        if (!contatos || typeof contatos !== "object") continue;
        for (const [numero, codigos] of Object.entries(contatos)) {
            const lista = Array.isArray(codigos) ? codigos : [codigos];
            const atualizacoes = [];

            for (const codigo of lista) {
                const status = await obterStatus(codigo);
                const chave = `${hash8(destinatarios)}|${hash8(numero)}|${codigo}`;
                if (ultimoStatus[chave] !== status) {
                    atualizacoes.push({ codigo, status });
                    ultimoStatus[chave] = status;
                }
            }

            if (!atualizacoes.length) continue;

            const linhas = atualizacoes
                .map(({ codigo, status }) => `✅ *Código:* ${codigo}\n   *Status:* ${status}`)
                .join("\n\n");

            const agora = new Date().toLocaleString("pt-BR", {
                day: "2-digit", month: "2-digit", year: "numeric",
                hour: "2-digit", minute: "2-digit",
            });

            const mensagem =
                `*🎉 RASTREAMENTO DE ENCOMENDA(S)*\n\n` +
                `${linhas}\n\n` +
                `🕒 ${agora}\n` +
                `_Enviado automaticamente._`;

            const numeroFormatado = numero.replace(/\D/g, "") + "@c.us";

            if (DRY_RUN) {
                console.log(
                    `[dry-run] envio suprimido telefone=${mascararNumero(numero)} destino=${hash8(destinatarios)}`
                );
            } else {
                try {
                    await client.sendMessage(numeroFormatado, mensagem);
                    console.log(`Mensagem enviada telefone=${mascararNumero(numero)} destino=${hash8(destinatarios)}`);
                } catch (e) {
                    console.error(`Erro ao enviar telefone=${mascararNumero(numero)} tipo=${tipoErro(e)}`);
                }
                await new Promise(r => setTimeout(r, 2_000));
            }
        }
    }

    console.log(`Proxima verificacao em ${INTERVALO / 1000}s...`);
}

function iniciarLoop() {
    verificarEEnviar();
    setInterval(verificarEEnviar, INTERVALO);
}

if (DRY_RUN) {
    console.log("Modo DRY_RUN ativo: WhatsApp nao sera inicializado e nenhuma mensagem sera enviada.");
    verificarEEnviar().finally(() => process.exit(0));
} else {
    client.initialize();
}
