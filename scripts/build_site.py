"""Construit le site statique de brainops.tech à partir de site/ (bibliothèque standard seulement).

    python scripts/build_site.py                          # build/site, pour https://brainops.tech
    python scripts/build_site.py --allow-placeholders     # aperçu local, mentions légales incomplètes

Les pages de site/ sont écrites au format des Artifacts (un <title>, un <style>, puis le contenu,
sans <!doctype> ni <head>) : le script les enveloppe dans un document complet, remplace les polices
Google par les polices servies par le site, et ajoute ce qu'un site public demande : métadonnées
pour les moteurs et les aperçus de liens, 404, robots.txt, sitemap.xml, en-têtes de sécurité
(_headers, lu par Cloudflare Pages).

Le build échoue tant que les mentions légales contiennent « [à compléter] » : un site
professionnel en France doit identifier son éditeur (LCEN, article 6).
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
PLACEHOLDER = "[à compléter]"

DESCRIPTION = ("BrainOps relie votre infrastructure, vos applications, SAP compris, vos identités et votre code "
               "à vos processus métier, pour voir en une seconde ce qui s'arrête quand un composant tombe.")

FONT_LINKS = re.compile(r'<link rel="preconnect"[^>]*>\s*|<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\s*')
TITLE = re.compile(r"^\s*<title>(.*?)</title>\s*", re.S)


def split_page(text: str) -> tuple[str, str, str]:
    """(titre, <style>…</style>, contenu) d'une page au format Artifact."""
    match = TITLE.match(text)
    if not match:
        raise SystemExit("la page doit commencer par <title>")
    rest = FONT_LINKS.sub("", text[match.end():])
    style_end = rest.index("</style>") + len("</style>")
    return html.unescape(match.group(1)), rest[:style_end].strip(), rest[style_end:].strip()


def document(title: str, style: str, body: str, *, domain: str, path: str, description: str,
             index: bool = True) -> str:
    url = f"{domain}{path}"
    image = f"{domain}/assets/og-brainops.jpg"
    robots = "" if index else '<meta name="robots" content="noindex">\n'
    esc = html.escape
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{robots}<link rel="canonical" href="{esc(url)}">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<meta name="theme-color" content="#0B1218">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="BrainOps">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/archivo-800-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
{style}
</head>
<body>
{body}
</body>
</html>
"""


HEADERS = """/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; script-src 'none'; connect-src 'none'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=604800

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Construit le site statique de BrainOps.")
    parser.add_argument("--domain", default="https://brainops.tech", help="adresse publique, sans / final")
    parser.add_argument("--out", default=str(ROOT / "build" / "site"))
    parser.add_argument("--allow-placeholders", action="store_true",
                        help="aperçu local : accepter des mentions légales incomplètes")
    args = parser.parse_args()
    domain = args.domain.rstrip("/")
    out = Path(args.out)

    legal_text = (SRC / "mentions-legales.html").read_text(encoding="utf-8")
    missing = legal_text.count(PLACEHOLDER)
    if missing and not args.allow_placeholders:
        print(f"Mentions légales incomplètes : {missing} champ(s) « {PLACEHOLDER} » dans site/mentions-legales.html.\n"
              "Les compléter avant la mise en ligne (ou --allow-placeholders pour un aperçu local).", file=sys.stderr)
        return 1

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SRC / "assets", out / "assets")

    # Accueil : chemins absolus (la page 404 est servie à n'importe quelle adresse) et lien vers les mentions légales.
    title, style, body = split_page((SRC / "index.html").read_text(encoding="utf-8"))
    body = body.replace('src="assets/', 'src="/assets/')
    body = body.replace("<span>Illustrations générées avec Nano Banana Pro</span>",
                        '<span>Illustrations générées avec Nano Banana Pro · <a href="/mentions-legales">Mentions légales</a></span>')
    if "/mentions-legales" not in body:
        raise SystemExit("pied de page introuvable : le lien vers les mentions légales n'a pas été ajouté")
    (out / "index.html").write_text(document(title, style, body, domain=domain, path="/", description=DESCRIPTION),
                                    encoding="utf-8")

    legal_title, legal_style, legal_body = split_page(legal_text)
    (out / "mentions-legales.html").write_text(
        document(legal_title, legal_style, legal_body, domain=domain, path="/mentions-legales",
                 description="Mentions légales du site BrainOps."), encoding="utf-8")

    not_found = """<main>
  <a href="/">← BrainOps</a>
  <h1>Cette page n'existe pas</h1>
  <p>L'adresse a peut-être changé. La page d'accueil présente BrainOps, le jumeau numérique du SI.</p>
  <p><a href="/">Revenir à l'accueil</a></p>
</main>"""
    (out / "404.html").write_text(
        document("Page introuvable · BrainOps", legal_style, not_found, domain=domain, path="/404",
                 description="Page introuvable.", index=False), encoding="utf-8")

    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {domain}/sitemap.xml\n", encoding="utf-8")
    today = date.today().isoformat()
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{domain}/</loc><lastmod>{today}</lastmod></url>\n"
        f"  <url><loc>{domain}/mentions-legales</loc><lastmod>{today}</lastmod></url>\n"
        "</urlset>\n", encoding="utf-8")
    (out / "_headers").write_text(HEADERS, encoding="utf-8")

    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    print(f"{len(files)} fichiers dans {out} pour {domain}")
    if missing:
        print(f"Attention : {missing} champ(s) « {PLACEHOLDER} » dans les mentions légales (aperçu seulement).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
