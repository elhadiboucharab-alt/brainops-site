# brainops-site

Site marketing de BrainOps, le jumeau numérique du SI : https://brainops.tech

Une seule source, `site/index.html`, d'où sortent deux versions :

| Version | Commande | Résultat | Guide |
|---|---|---|---|
| Site statique (Cloudflare Pages) | `python scripts/build_site.py` | `build/site/` | [docs/site.md](docs/site.md) |
| Thème WordPress | `python scripts/build_wp_theme.py` | `build/brainops-theme.zip` | [docs/wordpress.md](docs/wordpress.md) |

Python 3.11 ou plus récent, bibliothèque standard seulement.

## Contenu

```
site/index.html            la page d'accueil (format Artifact : <title>, <style>, contenu)
site/mentions-legales.html les mentions légales, à compléter avant la mise en ligne
site/assets/               logo, illustrations, image d'aperçu de lien, polices (Archivo, IBM Plex)
site/wordpress/            vignette du thème WordPress
scripts/                   builds et récupération des polices
marketing/                 visuels pour les réseaux sociaux
```

Le site ne dépose aucun cookie, n'appelle aucun service tiers (polices servies par le site) et n'a pas de formulaire.

## Avant la mise en ligne

- Compléter `site/mentions-legales.html` : le build du site statique refuse de produire le site tant qu'il reste des champs « [à compléter] ».

## Aperçu local

```bash
python scripts/build_site.py --allow-placeholders --domain http://127.0.0.1:8765
cd build/site && python -m http.server 8765
```

Les illustrations ont été générées avec Nano Banana Pro (Google Gemini). Les polices sont sous licence SIL Open Font License.
