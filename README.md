# 📦 WhatsApp Rastreio 2.0



![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)

![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)



![Status](https://img.shields.io/badge/Status-Versão_Demonstrativa-success)

![License](https://img.shields.io/badge/Licença-Proprietária-red)



## 📖 Sobre o projeto



O **WhatsApp Rastreio 2.0** é um sistema Full Stack desenvolvido para automatizar o acompanhamento de encomendas e o envio de notificações de rastreamento pelo WhatsApp.



O projeto surgiu da necessidade de reduzir tarefas manuais e repetitivas, centralizar informações de rastreamento e automatizar a comunicação com destinatários.



Sua arquitetura combina um servidor Python, um dashboard web, um bot desenvolvido em JavaScript e aplicações desktop para gerenciamento dos serviços.



### Versão de portfólio



Este repositório apresenta uma edição demonstrativa e independente do sistema original.



Por motivos de segurança, privacidade e propriedade intelectual, as integrações proprietárias foram removidas e substituídas por simulações.



Nenhuma mensagem real é enviada, nenhuma sessão do WhatsApp é iniciada e nenhuma API externa de rastreamento é consultada.



## 🎯 Objetivos



\- Automatizar processos repetitivos.

\- Centralizar o gerenciamento de encomendas.

\- Facilitar o acompanhamento de rastreamentos.

\- Demonstrar a integração entre diferentes tecnologias.

\- Aplicar boas práticas de segurança de software.

\- Desenvolver uma solução modular e de fácil manutenção.



## 🚀 Funcionalidades



### Dashboard administrativo



\- Cadastro e gerenciamento de destinatários.

\- Cadastro de números de contato.

\- Gerenciamento de múltiplos códigos de rastreamento.

\- Identificação de transportadoras por padrões de códigos.

\- Indicadores de destinatários, contatos e rastreamentos.

\- Exclusão de registros com confirmação.

\- Interface responsiva em tema escuro.

\- Autenticação de acesso.



### Bot de rastreamento



\- Processamento automatizado de encomendas.

\- Simulação de consultas de rastreamento.

\- Identificação de alterações de status.

\- Geração de mensagens formatadas.

\- Estrutura de integração com WhatsApp Web.

\- Tratamento de falhas.

\- Mascaramento de informações sensíveis nos logs.

\- Modo demonstrativo permanente.



### Aplicações desktop



\- Launcher gráfico para o servidor Flask.

\- Launcher gráfico para o bot Node.js.

\- Gerenciamento de processos.

\- Visualização de logs.

\- Detecção de ambientes Python e Node.js.

\- Estrutura para gerenciamento de QR Code.

\- Compilação de launchers em executáveis Windows.



## 🛠️ Tecnologias utilizadas



| Tecnologia | Aplicação |

|---|---|

| Python | Backend e aplicações desktop |

| Flask | Servidor web e rotas HTTP |

| JavaScript | Automação e lógica do bot |

| Node.js | Ambiente de execução |

| HTML5 | Estrutura da interface |

| CSS3 | Estilização e responsividade |

| Jinja2 | Renderização dinâmica de templates |

| Tkinter | Interfaces gráficas desktop |

| Puppeteer | Automação de navegador |

| WhatsApp Web.js | Estrutura de integração com WhatsApp |

| Axios | Comunicação HTTP |

| PyInstaller | Compilação de executáveis |

| Patch-package | Correções de dependências |

| Git e GitHub | Controle de versão |



## 🏗️ Arquitetura do sistema



```mermaid

flowchart TD

&#x20;   A[Usuário] --> B[Dashboard Web]

&#x20;   B --> C[Servidor Flask]

&#x20;   C --> D[Armazenamento JSON]

&#x20;   E[Bot Node.js] --> F[Dados fictícios]

&#x20;   F --> G[Simulador de rastreamento]

&#x20;   G --> H[Processamento de notificações]

&#x20;   H --> I[Simulação de envio]

&#x20;   J[Launcher Flask] --> C

&#x20;   K[Launcher Node.js] --> E

```



A arquitetura separa as responsabilidades entre interface, gerenciamento de dados, automação e integração de serviços.



Na edição demonstrativa, o bot utiliza dados fictícios em vez dos dados operacionais do dashboard.



## 📂 Estrutura do projeto



```text

Whatsapp-Rastreio/

│

├── static/

│   ├── app.js

│   └── style.css

│

├── templates/

│   └── index.html

│

├── patches/

│   └── whatsapp-web.js+1.34.8.patch

│

├── app.py

├── whatsapp-rastreio.js

├── launcher_flask.py

├── launcher_node.py

├── Bot WhatsApp.spec

├── Servidor Flask.spec

├── build.bat

├── package.json

├── package-lock.json

├── .env.example

├── .gitignore

└── README.md

```



## 🔐 Segurança e privacidade



O projeto incorpora medidas de segurança voltadas à proteção das configurações, autenticação e prevenção de vulnerabilidades.



### Medidas implementadas



\- Armazenamento de credenciais em variáveis de ambiente.

\- Hashing de senhas com scrypt.

\- Comparação segura de credenciais.

\- Autenticação HTTP Basic no dashboard.

\- Autenticação Bearer para comunicação entre serviços.

\- Proteção contra Cross-Site Request Forgery (CSRF).

\- Medidas de prevenção contra Cross-Site Scripting (XSS).

\- Validação de entradas.

\- Content Security Policy (CSP).

\- Cabeçalhos HTTP de segurança.

\- Validação de destinos de requisições.

\- Bloqueio de redirecionamentos HTTP nas requisições do bot.

\- Sanitização de informações sensíveis nos logs.

\- Restrição do servidor ao localhost por padrão.

\- Exclusão de credenciais e sessões do controle de versão.

\- Auditoria de dependências.



O armazenamento local utiliza JSON e não possui criptografia em repouso. A versão demonstrativa deve ser utilizada exclusivamente com dados fictícios.



## ⚙️ Instalação



### Pré-requisitos



\- Windows.

\- Node.js 22.

\- Python 3.10 ou superior.

\- Git.

\- Tkinter, caso sejam utilizados os launchers gráficos.



### 1. Instalar as dependências



Dependências JavaScript:



```bash

npm ci

```



Dependências Python:



```bash

python -m pip install flask pyinstaller

```



### 2. Configurar o ambiente



No PowerShell:



```powershell

Copy-Item .env.example .env

```



Configure as variáveis necessárias no arquivo `.env`.



| Variável | Finalidade |

|---|---|

| SECRET_KEY | Chave secreta do Flask |

| DASH_USER | Usuário do dashboard |

| DASH_PASSWORD_HASH | Hash da senha |

| DADOS_TOKEN | Token de autenticação entre serviços |

| TRACKING_MOCK_STATUS | Status simulado de rastreamento |

| HOST | Endereço do servidor |

| PORT | Porta do servidor |

| BROWSER_PATH | Caminho opcional do navegador |



As instruções para geração das credenciais locais estão disponíveis no `.env.example`.



**Nunca utilize credenciais de produção nesta demonstração.**



### 3. Executar o servidor



```bash

python app.py

```



Acesse o dashboard em:



http://127.0.0.1:5000



### 4. Executar o bot demonstrativo



```bash

npm start

```



O bot realizará uma simulação de rastreamento e encerrará sua execução sem enviar mensagens reais.



## 🖥️ Executáveis Windows



Os launchers podem ser compilados utilizando o PyInstaller.



```powershell

python -m PyInstaller --onefile --noconsole --name "Servidor Flask" launcher_flask.py

```



```powershell

python -m PyInstaller --onefile --noconsole --name "Bot WhatsApp" launcher_node.py

```



Os executáveis serão gerados na pasta `dist`.



Copie-os para a raiz do projeto antes da execução.



Os launchers dependem dos ambientes Python e Node.js instalados no computador.



## 🧪 Validação e testes



Durante o desenvolvimento e a manutenção do sistema, foram realizados processos de validação envolvendo:



\- Testes automatizados.

\- Testes de autenticação.

\- Testes de integração.

\- Validação de entradas.

\- Auditoria de segurança.

\- Simulação de rastreamentos.

\- Verificação de dependências.

\- Testes de persistência de sessão no sistema original.

\- Correção de incompatibilidades entre bibliotecas.

\- Reinstalação limpa de dependências.



A edição de portfólio foi adaptada para executar o fluxo demonstrativo sem acessar serviços proprietários ou enviar mensagens reais.



## 🧠 Competências demonstradas



Este projeto reúne conhecimentos práticos de:



\- Engenharia de Software.

\- Desenvolvimento Full Stack.

\- Desenvolvimento Backend.

\- Desenvolvimento Frontend.

\- Automação de processos.

\- Integração de APIs.

\- Segurança de aplicações.

\- Autenticação e autorização.

\- Arquitetura de sistemas.

\- Desenvolvimento desktop.

\- Programação assíncrona.

\- Tratamento de exceções.

\- Depuração de software.

\- Gerenciamento de dependências.

\- Controle de versão.

\- Manutenção e evolução de sistemas.



## 📈 Melhorias futuras



\- Ampliação da cobertura de testes.

\- Integração contínua com GitHub Actions.

\- Migração do armazenamento JSON para banco de dados.

\- Criptografia de dados armazenados.

\- Containerização com Docker.

\- Melhorias na acessibilidade da interface.

\- Aprimoramento do gerenciamento de processos.

\- Implementação de adaptadores genéricos de rastreamento.

\- Avaliação de APIs oficiais para mensageria.



## 👨‍💻 Desenvolvedores



### Íkaro Henrique Marçal Alexandre



Estudante de Engenharia de Software na Universidade Tecnológica Federal do Paraná (UTFPR).



[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/IkaroHenrique1306)



### Matheus Kioshi Fernandes Numata



Coautor e desenvolvedor do projeto.



## ⚠️ Aviso



Este repositório possui finalidade demonstrativa, educacional e de apresentação profissional.



O projeto utiliza bibliotecas de integração não oficial com o WhatsApp e não possui vínculo, associação ou aprovação da Meta.



A edição disponibilizada neste repositório não realiza envios reais de mensagens nem consultas a serviços proprietários de rastreamento.



## 📄 Direitos autorais



Copyright © 2025 — Íkaro Henrique Marçal Alexandre e Matheus Kioshi Fernandes Numata.



Todos os direitos reservados.



Este projeto não possui licença de código aberto concedida. A disponibilização do código para visualização não concede autorização irrestrita para reprodução, distribuição, modificação ou exploração comercial.



\---



**WhatsApp Rastreio 2.0**



*Transformando processos manuais em soluções automatizadas por meio da Engenharia de Software.*

