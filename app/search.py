from __future__ import annotations
from pathlib import Path
from datetime import date, datetime
from typing import Iterable, List, Optional, Dict
import os

from .config import BASE_PATH, DEFAULT_LIMIT


def _month_prefixes_between(start: date, end: date) -> List[str]:
    """Gera uma lista de prefixos YYYY-MM entre duas datas (inclusive)."""
    if start > end:
        start, end = end, start
    prefixes: List[str] = []
    y, m = start.year, start.month
    while (y < end.year) or (y == end.year and m <= end.month):
        prefixes.append(f"{y:04d}-{m:02d}")
        # avança mês
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1
    return prefixes


def _iter_month_dirs(base_dir: Path, month_prefixes: Optional[List[str]]) -> Iterable[Path]:
    """Itera pelos diretórios de primeiro nível do base que casam com os prefixos.
    Se month_prefixes for None, retorna todos os diretórios de primeiro nível.
    """
    try:
        with os.scandir(base_dir) as it:
            for entry in it:
                if not entry.is_dir():
                    continue
                name = entry.name
                if month_prefixes is None or any(name.startswith(p) for p in month_prefixes):
                    yield Path(entry.path)
    except FileNotFoundError:
        return


def _find_in_out_dirs(month_dir: Path) -> Iterable[Path]:
    """Encontra diretórios chamados IN ou OUT em qualquer profundidade sob month_dir."""
    # Caminhos típicos: <base>/<YYYY-MM...>/**/(IN|OUT)
    for sub in month_dir.rglob("*"):
        if sub.is_dir() and sub.name.upper() in ("IN", "OUT"):
            yield sub


def buscar(
    numero: str,
    month: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict]:
    """
    Busca arquivos dentro de IN/OUT cujo nome contenha `numero`.
    Filtro por período:
      - `month` no formato YYYY-MM, ou
      - `start` e `end` no formato YYYY-MM-DD (inclusivo), que serão convertidos em meses.
    Retorna no máx. `limit` itens com metadados (nome, tamanho, mtime, caminho relativo).
    """
    numero = str(numero).strip()
    if not numero:
        return []

    # Processa período
    month_prefixes: Optional[List[str]] = None
    if month:
        month_prefixes = [month]
    elif start and end:
        try:
            d1 = datetime.strptime(start, "%Y-%m-%d").date()
            d2 = datetime.strptime(end, "%Y-%m-%d").date()
            month_prefixes = _month_prefixes_between(d1, d2)
        except ValueError:
            month_prefixes = None

    results: List[Dict] = []
    max_items = limit or DEFAULT_LIMIT

    for month_dir in _iter_month_dirs(BASE_PATH, month_prefixes):
        for inout_dir in _find_in_out_dirs(month_dir):
            # Procurar arquivos cujo nome contenha o número
            try:
                for path in inout_dir.rglob(f"*{numero}*"):
                    if path.is_file():
                        rel = path.relative_to(BASE_PATH)
                        stat = path.stat()
                        results.append({
                            "name": path.name,
                            "path": str(rel).replace("\\", "/"),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                        })
                        if len(results) >= max_items:
                            return results
            except (PermissionError, FileNotFoundError):
                continue

    return results
