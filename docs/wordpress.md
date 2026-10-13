# Site BrainOps sur WordPress

Le site existe aussi sous forme de thème WordPress, généré depuis la même source que la version statique (`site/index.html`) : même page d'accueil, mêmes polices servies par le site, mêmes images. Les autres pages (mentions légales) s'écrivent dans l'administration WordPress et prennent la même identité.

```bash
python scripts/build_wp_theme.py
```

produit `build/brainops-theme.zip` (environ 3,6 Mo) et le dossier `build/wordpress/brainops/`.

## Ce que contient le thème

| Fichier | Rôle |
|---|---|
| `front-page.php` | la page d'accueil, quelle que soit la page d'accueil réglée dans WordPress |
| `header.php`, `footer.php` | barre du haut et pied de page ; les liens de sections mènent à l'accueil depuis n'importe quelle page, le pied de page mène aux mentions légales |
| `index.php`, `404.php` | les pages ordinaires et la page introuvable |
| `functions.php` | feuille de style, titre et métadonnées de l'accueil (description, aperçu de lien 1200 × 630), icône ; désactive les émojis de WordPress, qui appellent un service tiers |
| `style.css`, `assets/` | styles, polices Archivo et IBM Plex (licence SIL Open Font), logo, images |

Testé sur WordPress 6 (PHP 8.2) en local : page d'accueil, polices, images, métadonnées, page des mentions légales, page introuvable ; aucune ressource chargée depuis un autre site.

## Installer

**WordPress installé chez un hébergeur (WordPress.org, chez OVH, o2switch, Hostinger…)** : Apparence › Thèmes › Ajouter › Téléverser un thème › choisir `brainops-theme.zip` › Installer › Activer. Si l'hébergeur limite les envois à 2 Mo, déposer le dossier `build/wordpress/brainops/` par FTP dans `wp-content/themes/`, puis l'activer.

**WordPress.com** : les thèmes personnalisés ne s'installent qu'avec une offre qui autorise les extensions et thèmes (Business ou supérieure).

Puis, une fois :

1. **Réglages › Permaliens** : choisir « Titre de la publication », pour des adresses comme `/mentions-legales/`.
2. **Pages › Ajouter** : une page « Mentions légales » dont l'adresse (slug) est `mentions-legales`, avec le texte ci-dessous complété.
3. **Réglages › Général** : titre du site « BrainOps », langue « Français ».
4. Ne pas ajouter d'extension de mesure d'audience ou de formulaire sans prévoir le bandeau de consentement qu'elle impose.

## Texte des mentions légales

À compléter puis coller dans la page (bloc « Titre » pour les intertitres) :

> **Éditeur du site** — Nom ou raison sociale : … · Forme juridique et capital, le cas échéant : … · Adresse : … · Immatriculation (RCS ou SIREN), le cas échéant : … · Contact : … · Directeur ou directrice de la publication : …
>
> **Hébergement** — Nom, adresse et téléphone de l'hébergeur du WordPress (indiqués dans le contrat d'hébergement).
>
> **Données personnelles et cookies** — Ce site ne dépose aucun cookie, n'utilise aucun outil de mesure d'audience et ne contient aucun formulaire. Les polices de caractères sont servies par le site lui-même. L'hébergeur conserve, pour la sécurité et le fonctionnement du service, des journaux techniques de connexion.
>
> **Propriété intellectuelle** — Les textes, le logo et les illustrations de ce site appartiennent à l'éditeur. Les illustrations ont été générées avec le modèle Nano Banana Pro de Google. Les polices Archivo et IBM Plex sont distribuées sous licence SIL Open Font License.

Le paragraphe sur les cookies n'est vrai que tant qu'aucune extension n'en dépose : WordPress lui-même n'en dépose qu'aux personnes connectées à l'administration.

## Mettre à jour

Modifier `site/index.html` (la source unique), relancer `python scripts/build_wp_theme.py`, puis téléverser le nouveau zip : WordPress propose de remplacer le thème installé. Une modification faite directement dans l'éditeur de thème de WordPress serait écrasée à la mise à jour suivante.

## Domaine brainops.tech

Chez l'hébergeur du WordPress : ajouter le domaine `brainops.tech`, puis, chez le registrar du domaine, faire pointer ses enregistrements DNS vers l'hébergeur (l'hébergeur indique lesquels). Activer le certificat HTTPS proposé par l'hébergeur, puis, dans WordPress, Réglages › Général : « Adresse web de WordPress » et « Adresse web du site » en `https://brainops.tech`. Le guide `docs/site.md` (Cloudflare Pages) n'est utile que pour la version statique.
