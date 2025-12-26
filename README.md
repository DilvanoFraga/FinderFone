# Recording Finder

Aplicação FastAPI + HTML estático para localizar e baixar gravações em disco local. A busca filtra por número (trecho no nome do arquivo) e período (mês `YYYY-MM` ou intervalo `YYYY-MM-DD`), percorrendo subpastas `IN` e `OUT`.

## Requisitos

- Python 3.10+ (funciona com 3.13)
- Windows (paths e exemplos focados em Windows)

## Estrutura

```text
app/
  api.py               # Endpoints FastAPI (UI, health, search, download, zip)
  search.py            # Lógica de busca no filesystem
  config.py            # Configurações (BASE_PATH, DEFAULT_LIMIT)
  static/index.html    # UI simples para busca e download
run.py                 # Entry-point Uvicorn
smoke_test.py          # Teste rápido de /health, /search e /download
```

## Configuração

- `FINDER_BASE_PATH` (opcional): caminho base onde estão as gravações.
  - Padrão: `C:\Recordings`.
- `FINDER_DEFAULT_LIMIT` (opcional): limite padrão de resultados (default `200`).

## Preparar ambiente (PowerShell)

```pwsh
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Como executar

### Opção 1 — VS Code Tasks

- Terminal > Run Task > "Start Finder" para iniciar
- Terminal > Run Task > "Open Finder UI" para abrir o navegador em `http://localhost:8000/`
- Terminal > Run Task > "Stop Finder" para parar

### Opção 2 — PowerShell direto

```pwsh
# (opcional) definir o diretório base
$env:FINDER_BASE_PATH = "C:\Recordings"  # ajuste conforme seu ambiente

# iniciar servidor
.\.venv\Scripts\python.exe run.py

# acessar UI
# http://localhost:8000/
```

## UI (Web)

- Abra `http://localhost:8000/`
- Preencha:
  - Número: obrigatório (ex.: `11999999999`)
  - Mês: `YYYY-MM` (ex.: `2025-01`) ou deixe vazio para usar `start/end`
  - Início/Fim: datas `YYYY-MM-DD`
  - Limite: número de itens a retornar (default 200)
- Ações por item: "Salvar como…" (File System Access API) e "Copiar caminho"
- Ação em massa: "Salvar tudo (.zip)"

## API

- `GET /health` → `{ status, base }`
- `GET /search` parâmetros:
  - `numero` (obrigatório)
  - `month` (`YYYY-MM`) ou `start` + `end` (`YYYY-MM-DD`)
  - `limit` (1..5000)
  - resposta: `{ count, items: [{ name, path, size, modified }] }`
- `GET /download?path=<rel>` → baixa um arquivo por caminho relativo ao `BASE_PATH`
- `POST /download-zip` body: `{ paths: [rel1, rel2, ...], zip_name?: "arquivos.zip" }`

## Smoke test (rápido)

```pwsh
. .venv/Scripts/Activate.ps1
.\.venv\Scripts\python.exe smoke_test.py
```

Saída esperada (exemplo):

```text
HEALTH 200 {"status": "ok", "base": "C:\\Recordings"}
SEARCH 200 2 items
DOWNLOAD 200 1006195
```

## Notas e Troubleshooting

- 500 ao buscar: verifique `FINDER_BASE_PATH` — precisa apontar para a raiz que contém pastas por mês (prefixo `YYYY-MM`).
- Permissões/antivírus: caminhos grandes/NTFS podem exigir permissões; antivírus pode atrasar ZIP ou downloads.
- Formato de mês: `month` deve ser exatamente `YYYY-MM` ou a API retorna 422.
- Performance: a busca é limitada por `limit` (default 200) para evitar varreduras muito grandes.
- ZIP grande: o servidor streama o ZIP; em browsers sem File System Access API, o arquivo é montado na memória do navegador.

## Dependências

- `fastapi`, `uvicorn[standard]`, `httpx` (apenas para o smoke test)

## Licença

Uso interno.
