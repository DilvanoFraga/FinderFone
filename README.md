# 🔍 FinderFone

> Aplicação FastAPI + HTML para localizar e baixar gravações de chamadas em disco local.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![VoIP](https://img.shields.io/badge/VoIP-Asterisk-F47A20?style=flat)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows)

Busca gravações por número de telefone e período (mês ou intervalo de datas), percorrendo subpastas `IN` e `OUT`. Suporta download individual ou em lote via ZIP.

---

## Funcionalidades

- 🔎 Busca por número (trecho no nome do arquivo) e período (`YYYY-MM` ou `YYYY-MM-DD`)
- 📥 Download individual via File System Access API
- 📦 Download em lote como `.zip`
- 🔗 Cópia de caminho de arquivo
- ⚡ API REST com FastAPI + Uvicorn

---

## Estrutura

```text
app/
  api.py            # Endpoints FastAPI (UI, health, search, download, zip)
  search.py         # Lógica de busca no filesystem
  config.py         # Configurações (BASE_PATH, DEFAULT_LIMIT)
  static/index.html # UI web para busca e download
run.py              # Entry-point Uvicorn
smoke_test.py       # Teste rápido de /health, /search e /download
```

---

## Instalação

**Requisitos:** Python 3.10+ · Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Variáveis de ambiente (opcionais):**

| Variável | Padrão | Descrição |
|---|---|---|
| `FINDER_BASE_PATH` | `C:\Recordings` | Raiz onde estão as gravações |
| `FINDER_DEFAULT_LIMIT` | `200` | Limite padrão de resultados |

---

## Como executar

**Via VS Code Tasks:**
- `Start Finder` — inicia o servidor
- `Open Finder UI` — abre `http://localhost:8000/` no navegador
- `Stop Finder` — encerra o servidor

**Via PowerShell:**
```powershell
$env:FINDER_BASE_PATH = "C:\Recordings"
.\.venv\Scripts\python.exe run.py
```

Acesse: `http://localhost:8000/`

---

## API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Status e base path |
| `GET` | `/search` | Busca gravações (`numero`, `month` ou `start`+`end`, `limit`) |
| `GET` | `/download` | Download de arquivo por caminho relativo |
| `POST` | `/download-zip` | Download em lote como ZIP |

---

## Smoke test

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe smoke_test.py
```

Saída esperada:
```
HEALTH 200 {"status": "ok", "base": "C:\\Recordings"}
SEARCH 200 2 items
DOWNLOAD 200 1006195
```

---

## Dependências

`fastapi` · `uvicorn[standard]` · `httpx` (smoke test)

---

## Licença

Uso interno.
