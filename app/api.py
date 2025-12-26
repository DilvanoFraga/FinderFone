from fastapi import FastAPI, HTTPException, Query
import re
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from pathlib import Path
from typing import Optional
import tempfile
import zipfile

from .config import BASE_PATH, DEFAULT_LIMIT
from .search import buscar

app = FastAPI(title="Recording Finder", version="0.1.0")
STATIC_DIR = Path(__file__).parent / "static"

@app.get("/health")
def health():
    return {"status": "ok", "base": str(BASE_PATH)}

@app.get("/search")
def search(
    numero: str = Query(..., description="Número para filtrar nos nomes dos arquivos"),
    month: Optional[str] = Query(None, description="Filtro YYYY-MM"),
    start: Optional[str] = Query(None, description="Início YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Fim YYYY-MM-DD"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=5000),
):
    if month and not re.fullmatch(r"\d{4}-\d{2}", month):
        raise HTTPException(status_code=422, detail="Parâmetro month deve ser YYYY-MM")
    items = buscar(numero=numero, month=month, start=start, end=end, limit=limit)
    return {"count": len(items), "items": items}

@app.get("/download")
def download(path: str = Query(..., description="Caminho relativo dentro do BASE_PATH")):
    base = BASE_PATH
    full = (base / path).resolve()
    try:
        full.relative_to(base)
    except ValueError:
        raise HTTPException(status_code=400, detail="Caminho inválido")

    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(str(full), filename=full.name)

@app.get("/", include_in_schema=False)
def index():
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        return HTMLResponse("<h1>UI não encontrada</h1>", status_code=500)
    return FileResponse(str(idx))

@app.post("/download-zip")
def download_zip(payload: dict):
    paths = payload.get("paths")
    zip_name = payload.get("zip_name", "arquivos.zip")
    if not isinstance(paths, list) or not paths:
        raise HTTPException(status_code=400, detail="'paths' obrigatório e deve ser lista")

    spooled = tempfile.SpooledTemporaryFile(max_size=100*1024*1024)

    def _dedup_name(name: str, used: dict) -> str:
        if name not in used:
            used[name] = 1
            return name
        base, dot, ext = name.rpartition('.')
        if not base:
            base, ext = name, ''
        count = used[name] + 1
        used[name] = count
        return f"{base} ({count}){dot}{ext}" if ext else f"{base} ({count})"

    used_names = {}
    with zipfile.ZipFile(spooled, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in paths:
            try:
                rel_str = str(rel)
                full = (BASE_PATH / rel_str).resolve()
                full.relative_to(BASE_PATH)
            except Exception:
                continue
            if full.exists() and full.is_file():
                # Apenas o arquivo no root do ZIP; resolver colisões de nome
                arc = _dedup_name(full.name, used_names)
                zf.write(str(full), arcname=arc)

    # calcular tamanho para Content-Length
    spooled.seek(0, 2)
    total_size = spooled.tell()
    spooled.seek(0)
    headers = {
        "Content-Disposition": f'attachment; filename="{zip_name}"',
        "Content-Length": str(total_size),
    }
    return StreamingResponse(spooled, media_type="application/zip", headers=headers)
