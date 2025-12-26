from pathlib import Path
import os

# Diretório base onde estão as gravações.
# Pode ser sobrescrito pela variável de ambiente FINDER_BASE_PATH.
BASE_PATH = Path(os.getenv("FINDER_BASE_PATH", r"C:\Recordings")).resolve()

# Limite padrão de resultados por busca
DEFAULT_LIMIT = int(os.getenv("FINDER_DEFAULT_LIMIT", "200"))
