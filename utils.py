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
    for p in NOISE_PATTERNS:
        s = re.sub(p, ' ', s, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', s).strip(' -')

def parse_filename(stem: str):
    """Devuelve (artista, título) parseando el nombre del archivo."""
    s = clean_stem(stem)
    parts = re.split(r'\s*-\s+', s, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, s.strip()
