"""Construit le thème WordPress « BrainOps » à partir de la page du site (bibliothèque standard seulement).

    python scripts/build_wp_theme.py        # build/wordpress/brainops/ et build/brainops-theme.zip

Une seule source : site/index.html. Le thème reprend sa feuille de style, ses polices servies
par le site et ses images ; la page d'accueil devient front-page.php, l'en-tête et le pied de page
deviennent header.php et footer.php, et index.php affiche les autres pages (mentions légales,
écrites dans l'administration WordPress) avec la même identité.

À téléverser dans WordPress : Apparence › Thèmes › Ajouter › Téléverser un thème. Voir docs/wordpress.md.
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
OUT = ROOT / "build" / "wordpress" / "brainops"
ZIP = ROOT / "build" / "brainops-theme.zip"
VERSION = "1.0.0"

THEME_URI = "<?php echo esc_url( get_template_directory_uri() ); ?>"

STYLE_HEADER = f"""/*
Theme Name: BrainOps
Theme URI: https://brainops.tech
Author: BrainOps
Description: Site de BrainOps, le jumeau numérique du SI. Page d'accueil fixe, pages simples (mentions légales) dans la même identité. Polices servies par le thème, sans appel à un service tiers.
Version: {VERSION}
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
Text Domain: brainops
*/
"""

# Pages ordinaires (mentions légales, etc.) et barre d'administration de WordPress.
EXTRA_CSS = """
/* Pages ordinaires : mentions légales et autres pages écrites dans WordPress */
.page-content { max-width: 760px; margin: 0 auto; padding-block: 56px 88px; display: grid; gap: 22px; }
.page-content h1 { font-size: clamp(2rem, 4vw, 2.6rem); }
.page-content h2 { font-size: 1.3rem; margin-top: 18px; }
.page-content p, .page-content li { color: var(--muted); }
.page-content strong, .page-content b { color: var(--ink); }
.page-content .entry > * + * { margin-top: 14px; }
footer a { color: var(--muted); }
/* Barre d'administration, visible quand on est connecté */
.admin-bar header.top { top: 32px; }
@media (max-width: 782px) { .admin-bar header.top { top: 46px; } }
"""

FUNCTIONS = """<?php
/**
 * Thème BrainOps : réglages, feuille de style, métadonnées de la page d'accueil.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'after_setup_theme', function () {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', array( 'style', 'script', 'navigation-widgets' ) );
	add_theme_support( 'responsive-embeds' );
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'brainops', get_stylesheet_uri(), array(), wp_get_theme()->get( 'Version' ) );
} );

// Pas d'appel au service d'émojis de WordPress : le site ne contacte aucun tiers.
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );

add_filter( 'pre_get_document_title', function ( $title ) {
	return is_front_page() ? 'BrainOps · Le jumeau numérique du SI' : $title;
} );

add_action( 'wp_head', function () {
	$uri = get_template_directory_uri();
	echo '<link rel="preload" href="' . esc_url( $uri . '/assets/fonts/archivo-800-latin.woff2' ) . '" as="font" type="font/woff2" crossorigin>' . "\\n";
	echo '<link rel="icon" type="image/png" href="' . esc_url( $uri . '/assets/favicon.png' ) . '">' . "\\n";
	echo '<meta name="theme-color" content="#0B1218">' . "\\n";
	if ( ! is_front_page() ) {
		return;
	}
	$description = __DESCRIPTION__;
	$title       = 'BrainOps · Le jumeau numérique du SI';
	$url         = home_url( '/' );
	$image       = $uri . '/assets/og-brainops.jpg';
	echo '<meta name="description" content="' . esc_attr( $description ) . '">' . "\\n";
	echo '<meta property="og:type" content="website">' . "\\n";
	echo '<meta property="og:locale" content="fr_FR">' . "\\n";
	echo '<meta property="og:site_name" content="BrainOps">' . "\\n";
	echo '<meta property="og:title" content="' . esc_attr( $title ) . '">' . "\\n";
	echo '<meta property="og:description" content="' . esc_attr( $description ) . '">' . "\\n";
	echo '<meta property="og:url" content="' . esc_url( $url ) . '">' . "\\n";
	echo '<meta property="og:image" content="' . esc_url( $image ) . '">' . "\\n";
	echo '<meta property="og:image:width" content="1200">' . "\\n";
	echo '<meta property="og:image:height" content="630">' . "\\n";
	echo '<meta name="twitter:card" content="summary_large_image">' . "\\n";
}, 5 );
"""

HEADER_PHP = """<?php
/**
 * En-tête : document, puis barre du haut (logo, sections de l'accueil, programme pilote).
 */
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
"""

FOOTER_PHP_TAIL = """
<?php wp_footer(); ?>
</body>
</html>
"""

INDEX_PHP = """<?php
/**
 * Pages ordinaires (mentions légales…) et repli pour tout autre contenu.
 */
get_header();
?>
<main id="haut" class="wrap page-content">
<?php
if ( have_posts() ) :
	while ( have_posts() ) :
		the_post();
		?>
		<article <?php post_class(); ?>>
			<h1><?php the_title(); ?></h1>
			<div class="entry"><?php the_content(); ?></div>
		</article>
		<?php
	endwhile;
else :
	?>
	<h1>Cette page n'existe pas</h1>
	<p><a href="<?php echo esc_url( home_url( '/' ) ); ?>">Revenir à l'accueil</a></p>
	<?php
endif;
?>
</main>
<?php
get_footer();
"""

NOT_FOUND_PHP = """<?php
/**
 * Page introuvable.
 */
get_header();
?>
<main id="haut" class="wrap page-content">
	<h1>Cette page n'existe pas</h1>
	<p>L'adresse a peut-être changé. La page d'accueil présente BrainOps, le jumeau numérique du SI.</p>
	<p><a href="<?php echo esc_url( home_url( '/' ) ); ?>">Revenir à l'accueil</a></p>
</main>
<?php
get_footer();
"""


def section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i) + len(end)
    return text[i:j]


def main() -> int:
    source = (SRC / "index.html").read_text(encoding="utf-8")
    if "<?" in source:
        raise SystemExit("site/index.html contient « <? » : incompatible avec un gabarit PHP")
    style = section(source, "<style>", "</style>")[len("<style>"):-len("</style>")].strip()
    header = section(source, '<header class="top">', "</header>")
    main_html = section(source, '<main id="haut">', "</main>")
    footer = section(source, "<footer>", "</footer>")

    # Les liens de section pointent vers l'accueil, pour fonctionner aussi depuis les autres pages.
    home = "<?php echo esc_url( home_url( '/' ) ); ?>"
    header = header.replace('href="#haut"', f'href="{home}"')
    header = re.sub(r'href="#([\w-]+)"', lambda m: f"href=\"<?php echo esc_url( home_url( '/#{m.group(1)}' ) ); ?>\"", header)
    header = header.replace('src="assets/', f'src="{THEME_URI}/assets/')
    main_html = main_html.replace('src="assets/', f'src="{THEME_URI}/assets/')
    legal = "<?php echo esc_url( home_url( '/mentions-legales/' ) ); ?>"
    footer = footer.replace("<span>Illustrations générées avec Nano Banana Pro</span>",
                            f'<span>Illustrations générées avec Nano Banana Pro · <a href="{legal}">Mentions légales</a></span>')
    if "mentions-legales" not in footer:
        raise SystemExit("pied de page introuvable : lien vers les mentions légales non ajouté")

    fonts_css = (SRC / "assets" / "fonts" / "fonts.css").read_text(encoding="utf-8")
    fonts_css = fonts_css.replace("url(/assets/fonts/", "url(assets/fonts/")  # relatif à style.css

    description = re.search(r'DESCRIPTION = \(\s*"(.*?)"\s*"(.*?)"\s*\)', (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8"), re.S)
    text = description.group(1) + description.group(2)
    php_description = "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(SRC / "assets", OUT / "assets")
    shutil.copy(SRC / "wordpress" / "screenshot.png", OUT / "screenshot.png")

    (OUT / "style.css").write_text(STYLE_HEADER + "\n" + fonts_css + "\n" + style + "\n" + EXTRA_CSS, encoding="utf-8")
    (OUT / "functions.php").write_text(FUNCTIONS.replace("__DESCRIPTION__", php_description), encoding="utf-8")
    (OUT / "header.php").write_text(HEADER_PHP + header + "\n", encoding="utf-8")
    (OUT / "footer.php").write_text(footer + FOOTER_PHP_TAIL, encoding="utf-8")
    (OUT / "front-page.php").write_text(
        "<?php\n/**\n * Page d'accueil, générée depuis site/index.html par scripts/build_wp_theme.py.\n */\nget_header();\n?>\n"
        + main_html + "\n<?php\nget_footer();\n", encoding="utf-8")
    (OUT / "index.php").write_text(INDEX_PHP, encoding="utf-8")
    (OUT / "404.php").write_text(NOT_FOUND_PHP, encoding="utf-8")

    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, Path("brainops") / path.relative_to(OUT))
    size = ZIP.stat().st_size / 1024
    print(f"Thème écrit dans {OUT} et {ZIP} ({size:.0f} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
