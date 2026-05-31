import re

NOISE_PATTERNS = [
    r'\b(audio|video|oficial|official|letra|lyrics|lyric[\s_]video|visualizer|'
    r'video[\s_]oficial|audio[\s_]oficial)\b',
    r'\bvol[\s_]*\d+\b',
    r'\b\d{4}\b',
    r'^\d+\s+',
    r'[^\x00-\x7Fá-ú\u00C0-\u024F\s\w\-]+',
    r'\s{2,}',
]

def safe_name(name: str) -> str:
    name = name.strip() or "Unknown"
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def clean_stem(stem: str) -> str:
    s = stem.replace('_', ' ')
    # Eliminar patrones de ruido
    for p in NOISE_PATTERNS:
        s = re.sub(p, ' ', s, flags=re.IGNORECASE)
    # Limpiar brackets y paréntesis sobrantes
    s = re.sub(r'[\(\[].*?[\)\]]', '', s)
    return re.sub(r'\s+', ' ', s).strip(' -')

def parse_filename(stem: str):
    """
    Devuelve (artista, título) parseando el nombre del archivo.
    Intenta detectar separadores comunes y colaboraciones.
    """
    s = clean_stem(stem)
    # Separadores comunes entre Artista - Título
    parts = re.split(r'\s*[\-–—]\s*', s, maxsplit=1)
    
    if len(parts) == 2:
        artist, title = parts[0].strip(), parts[1].strip()
        # Si el artista tiene "x" o "&", nos quedamos con el principal para el mapeo
        main_artist = re.split(r'\s+(?:x|&|ft\.?|feat\.?)\s+', artist, flags=re.IGNORECASE)[0]
        return main_artist.strip(), title
    
    return None, s.strip()
