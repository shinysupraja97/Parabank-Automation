from pathlib import Path

def load_properties(filepath: str) -> dict:
    cfg = {}
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Config file missing: {filepath}")
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg
