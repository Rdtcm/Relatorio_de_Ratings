# 📊 Relatório de Ações de Rating — Gerador de PDF

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-Internal%20Use-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Aplicação desktop para **coletar automaticamente ações de rating**, processar os dados e **gerar um relatório em PDF**, exibido em uma interface gráfica simples para o usuário.

## < / > Funcionalidades

- **Web scraping automatizado** das ações de rating publicadas
- **Extração e normalização inteligente** de dados financeiros
- **Geração de relatório PDF** com layout profissional
- **Interface gráfica intuitiva** com visualizador de PDF integrado
- **Distribuição simplificada** via executável standalone
- **Processamento em segundo plano** sem travar a interface

## 🏗️ Arquitetura do Sistema

```
Interface (PyQt5)
        ↓
     main.py (orquestração)
        ↓
Web Scraping (Playwright)
        ↓
 Processamento de dados
        ↓
Geração de PDF (ReportLab)
        ↓
 Exibição do relatório
```

## 📁 Estrutura do Projeto

```
project/
│
├── client_interface.py     # Interface gráfica principal
├── main.py                # Orquestrador do fluxo
├── scrapping_rating_actions.py  # Módulo de scraping
├── generate_pdf.py        # Gerador de PDF
│
├── output/
│   └── ratings.pdf       # PDF gerado
│
├── requirements.txt      # Dependências do projeto
└── README.md            # Este arquivo
```

## 🔧 Módulos Principais

### 🕷️ Módulo de Web Scraping (`scrapping_rating_actions.py`)

**Responsabilidades:**
- Acessa a página de ações de rating
- Filtra resultados relevantes
- Ignora emissões de dívida irrelevantes
- Abre apenas ações de **emissor**
- Extrai dados estruturados:
  - Empresa/Emissor
  - Agência de rating
  - Rating atual e anterior
  - Outlook atual e anterior
  - Ação de rating (upgrade/downgrade)
  - Data da ação
  - Link para detalhes

**Tecnologias utilizadas:**
- Playwright para automação de navegador
- Chromium em modo headless
- Expressões regulares para parsing textual
- Tratamento robusto de exceções

**Tratamentos implementados:**
- ✅ Ignora emissões de dívida não relevantes
- ✅ Deduplicação de registros duplicados
- ✅ Correção automática de nomes corporativos
- ✅ Fallback textual quando tabelas não existem
- ✅ Timeout e retry para conexões instáveis

### 📄 Módulo de Geração de PDF (`generate_pdf.py`)

**Responsabilidades:**
- Conversão de dados extraídos em tabela formatada
- Aplicação de layout padronizado e corporativo
- Uso de cores por tipo de ação (upgrade/downgrade)
- Geração de PDF em orientação horizontal
- Inclusão de metadados e timestamp

**Informações exibidas no relatório:**
- Data de geração
- Emissor/empresa
- Agência de rating
- Rating anterior
- Rating atual
- Ação de rating
- Fonte dinâmica das agências

**Bibliotecas utilizadas:**
- ReportLab para criação de PDF
- Pandas para manipulação de dados

### 🖥️ Interface Gráfica (`client_interface.py`)

**Tecnologias:**
- PyQt5 para interface nativa
- QWebEngineView para exibição de PDF integrada
- QThread para processamento em background

**Fluxo do usuário:**
1. Usuário abre a aplicação
2. Clica em "Gerar PDF"
3. Scraping e processamento ocorrem em segundo plano
4. Barra de progresso indica status
5. PDF é exibido automaticamente na interface
6. Opção para salvar ou imprimir

## ⚙️ Orquestração (`main.py`)

**Responsabilidades:**
1. Coordenação entre módulos
2. Execução do pipeline completo
3. Tratamento de erros global
4. Retorno do caminho do arquivo gerado

## 📋 Requisitos do Sistema

- **Python:** 3.11 ou superior
- **pip:** Gerenciador de pacotes Python
- **Sistema operacional:**
  - Windows 10/11
  - Linux (distribuições baseadas em Debian/Ubuntu)
  - macOS 10.15+

## 🚀 Instalação e Execução

### 1) Clonar o repositório
```bash
git clone <url-do-repositorio>
cd project
```

### 2) Criar ambiente virtual
**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3) Instalar dependências
```bash
pip install -r requirements.txt
```

### 4) Instalar navegador do Playwright
```bash
playwright install chromium
```

### 5) Executar aplicação
```bash
python client_interface.py
```

## 📦 Gerar Executável (Binário)

### Usando PyInstaller

1. **Instalar PyInstaller:**
```bash
pip install pyinstaller
```

2. **Gerar executável:**
```bash
pyinstaller --onefile --noconsole \
  --name RatingReport \
  --collect-all PyQt5 \
  --collect-all PyQt5.QtWebEngineWidgets \
  --collect-all PyQt5.QtWebEngineCore \
  --collect-all playwright \
  client_interface.py

```

3. **O executável será criado em:**
```
dist/client_interface.exe  (Windows)
dist/client_interface      (Linux/macOS)
```

## 👤 Para Usuários Finais

Caso queira apenas utilizar a ferramenta sem instalar Python:

### 📥 Download do executável:
[Clique aqui para baixar](https://drive.google.com/file/d/1w10o30uyRBSYQnhxPdcCBzcR_syyN5sT/view?usp=sharing)

**Instruções:**
1. Baixe o arquivo executável
2. Execute diretamente (Windows)
3. Para Linux/macOS, conceda permissões de execução:
```bash
chmod +x client_interface
./client_interface
```

## 🔄 Fluxo de Execução Interno

1. **Interface** inicia processo
2. **Thread worker** é criada para não travar UI
3. **main()** orquestra o pipeline
4. **Scraper** coleta dados da web
5. **Processamento** normaliza e filtra dados
6. **Geração do PDF** cria relatório formatado
7. **Visualização** exibe PDF automaticamente

## ⚠️ Observações Importantes

- **Primeira execução** pode ser mais lenta devido à instalação do navegador
- **Conexão com internet** é necessária para scraping
- Mudanças no **site de origem** podem exigir ajustes no código
- Recomendado executar em **ambiente virtual Python**
- Verifique permissões de escrita na pasta de saída

## 👨🏻‍💻 Suporte e Contato

Caso encontre problemas ou tenha sugestões:

**Contato:** 📧 ledoryan42@gmail.com

**Relatar issues:**
1. Descreva o problema encontrado
2. Inclua mensagens de erro (se houver)
3. Especifique sistema operacional e versão
4. Inclua passos para reproduzir o problema

## 📄 Licença

Uso interno e educacional. Para distribuição externa, ajustar conforme política de licenciamento da organização.

**Restrições:**
- Não redistribuir sem autorização
- Uso comercial requer licenciamento
- Modificações devem manter atribuição

## ✅ Benefícios e Resultados

A ferramenta proporciona:

- ✔️ **Coleta automática** sem intervenção manual
- ✔️ **Padronização de dados** de múltiplas fontes
- ✔️ **Relatório visual profissional** pronto para apresentação
- ✔️ **Uso simplificado** por usuários não técnicos
- ✔️ **Economia de tempo** em processos manuais
- ✔️ **Consistência** na formatação e apresentação
- ✔️ **Distribuição fácil** via executável standalone


## 🤓☝️ Imagens da Interface 
<img width="769" height="559" alt="image" src="https://github.com/user-attachments/assets/93c783bc-66ca-4c71-999f-fd769e8d4b75" />

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
**Desenvolvedor:** Ryan Ledo
