"""Télécharge une fois les polices du site (licence SIL Open Font) pour les servir depuis brainops.tech.

Servies par le site lui-même, elles évitent d'envoyer l'adresse IP des visiteurs à Google
(Google Fonts chargé depuis Google pose une question RGPD pour un site européen).

    python scripts/fetch_site_fonts.py

Écrit site/assets/fonts/*.woff2 et site/assets/fonts/fonts.css (sous-ensembles latin et
latin-ext seulement : le site est en français). À relancer seulement si les polices changent.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

CSS_URL = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112,600;112,800"
           "&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap")
# Un navigateur récent : Google renvoie alors du woff2.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
KEEP = {"latin", "latin-ext"}
OUT = Path(__file__).resolve().parent.parent / "site" / "assets" / "fonts"


def get(url: str) -> bytes:
    if not url.startswith(("https://fonts.googleapis.com/", "https://fonts.gstatic.com/")):
        raise SystemExit(f"adresse inattendue : {url}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def main() -> None:
    css = get(CSS_URL).decode("utf-8")
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css)
    if not blocks:
        raise SystemExit("aucune règle @font-face trouvée")
    OUT.mkdir(parents=True, exist_ok=True)
    out_css = []
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        url = re.search(r"src:\s*url\(([^)]+)\)", block).group(1)
        name = f"{family.lower().replace(' ', '-')}-{weight}-{subset}.woff2"
        (OUT / name).write_bytes(get(url))
        out_css.append(re.sub(r"url\([^)]+\)", f"url(/assets/fonts/{name})", block))
        print(f"{name}")
    (OUT / "fonts.css").write_text("\n".join(out_css) + "\n", encoding="utf-8")
    print(f"{len(out_css)} faces écrites dans {OUT}")


if __name__ == "__main__":
    sys.exit(main())
