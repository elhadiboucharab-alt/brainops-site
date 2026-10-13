# Site public : brainops.tech

Le site marketing est une page statique : `site/index.html` (au format des Artifacts, publiée aussi en aperçu privé) et ses images dans `site/assets/`. `scripts/build_site.py` en fait un site autonome dans `build/site/`, hébergé sur Cloudflare Pages.

## Ce que fait le build

```bash
python scripts/build_site.py                        # pour https://brainops.tech
python scripts/build_site.py --allow-placeholders   # aperçu local
```

- enveloppe chaque page dans un document complet : langue, description, adresse canonique, aperçu de lien (LinkedIn, messageries) avec `assets/og-brainops.jpg` en 1200 × 630, icône ;
- remplace les polices Google par les polices servies par le site (`site/assets/fonts/`, récupérées une fois avec `scripts/fetch_site_fonts.py`) : aucune adresse IP de visiteur n'est envoyée à Google ;
- ajoute la page des mentions légales, une page 404, `robots.txt`, `sitemap.xml` et `_headers` (en-têtes de sécurité et de cache lus par Cloudflare Pages : HTTPS forcé, politique de sécurité du contenu sans script ni ressource externe, pas d'intégration dans un autre site) ;
- **refuse de produire le site tant que les mentions légales contiennent `[à compléter]`** : un site professionnel en France doit identifier son éditeur (LCEN, article 6). L'option `--allow-placeholders` sert seulement aux aperçus locaux.

Le site ne dépose aucun cookie et n'a ni formulaire ni mesure d'audience : pas de bandeau de consentement à prévoir.

## Mise en ligne, une fois

1. **Compléter les mentions légales** dans `site/mentions-legales.html` (éditeur, adresse, immatriculation le cas échéant, contact, directeur de la publication), puis vérifier : `python scripts/build_site.py` doit réussir.
2. **Acheter le domaine** `brainops.tech` (disponible le 13 octobre 2026 d'après l'annuaire RDAP). Le plus simple : l'acheter directement chez Cloudflare Registrar, qui le relie à Cloudflare sans réglage DNS. Chez un autre registrar, faire ensuite pointer ses serveurs de noms vers Cloudflare (l'étape 4 les indique).
3. **Créer le projet Cloudflare Pages** : tableau de bord Cloudflare → Workers & Pages → Créer → Pages → Connecter à Git → dépôt `elhadiboucharab-alt/brainops-site` (s'il est privé : autoriser l'application Cloudflare sur ce dépôt seulement). Réglages :

   | Réglage | Valeur |
   |---|---|
   | Branche de production | `main` |
   | Préréglage | Aucun |
   | Commande de build | `python scripts/build_site.py` |
   | Dossier de sortie | `build/site` |
   | Variable d'environnement | `PYTHON_VERSION` = `3.12` |

   Le script n'utilise que la bibliothèque standard de Python : rien à installer pendant le build.
4. **Brancher le domaine** : projet Pages → Domaines personnalisés → ajouter `brainops.tech`, puis `www.brainops.tech`. Si le domaine est chez Cloudflare, les enregistrements DNS sont créés automatiquement, et le certificat HTTPS suit en quelques minutes.
5. **Rediriger www** : Règles → Règles de redirection → `www.brainops.tech/*` vers `https://brainops.tech/${1}` (301), pour une seule adresse canonique.
6. **Vérifier** : la page s'affiche en HTTPS, `https://brainops.tech/mentions-legales` aussi, et l'aperçu du lien dans l'inspecteur de publication LinkedIn montre l'image et le titre.

Ensuite, chaque `git push` sur `main` redéploie le site ; chaque autre branche obtient une adresse d'aperçu. 

## Une adresse de contact

Le site et la présentation n'ont pas encore d'adresse de contact. Avec le domaine chez Cloudflare, **Email Routing** (gratuit) crée par exemple `contact@brainops.tech` et transfère les messages vers une boîte existante, sans serveur de messagerie. Une fois l'adresse choisie, l'ajouter dans la section « Programme pilote » de `site/index.html`, dans les mentions légales et sur la dernière diapositive.

## Mettre à jour le site

Modifier `site/index.html` (ou ajouter une image dans `site/assets/`), vérifier avec `python scripts/build_site.py --allow-placeholders --domain http://127.0.0.1:8765` et `python -m http.server 8765` dans `build/site`, puis pousser sur `main`. En local, ouvrir `mentions-legales.html` avec son extension : Cloudflare Pages sert la même page à l'adresse `/mentions-legales`.
