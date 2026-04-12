# -*- coding: utf-8 -*-
"""
Module utilitaire pour RGAA Section 2 Tester

Fonctions utilitaires diverses pour le traitement d'URLs, de texte, etc.
"""

import platform
import re
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse


def normaliser_url(url: str) -> str:
    """
    Normalise une URL pour éviter les doublons.

    Args:
        url: URL à normaliser.

    Returns:
        URL normalisée.
    """
    # Supprimer les espaces
    url = url.strip()

    # Ajouter le protocole si manquant
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Parser l'URL
    parsed = urlparse(url)

    # Reconstruire l'URL normalisée (sans fragment)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or '/'

    # Supprimer le slash final sauf pour la racine
    if path != '/' and path.endswith('/'):
        path = path[:-1]

    return f"{scheme}://{netloc}{path}"


def est_url_valide(url: str) -> bool:
    """
    Vérifie si une URL est valide.

    Args:
        url: URL à vérifier.

    Returns:
        True si l'URL est valide, False sinon.
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except Exception:
        return False


def extraire_domaine(url: str) -> str:
    """
    Extrait le domaine d'une URL.

    Args:
        url: URL complète.

    Returns:
        Domaine de l'URL.
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def construire_url_absolue(base_url: str, relative_url: str) -> str:
    """
    Construit une URL absolue à partir d'une URL de base et d'une URL relative.

    Args:
        base_url: URL de base.
        relative_url: URL relative.

    Returns:
        URL absolue.
    """
    return urljoin(base_url, relative_url)


def est_meme_domaine(url1: str, url2: str) -> bool:
    """
    Vérifie si deux URLs appartiennent au même domaine.

    Args:
        url1: Première URL.
        url2: Deuxième URL.

    Returns:
        True si même domaine, False sinon.
    """
    return extraire_domaine(url1) == extraire_domaine(url2)


def nettoyer_texte(texte: str) -> str:
    """
    Nettoie un texte en supprimant les espaces superflus.

    Args:
        texte: Texte à nettoyer.

    Returns:
        Texte nettoyé.
    """
    if not texte:
        return ""
    # Remplacer les retours à la ligne et espaces multiples par un seul espace
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()


def tronquer_texte(texte: str, max_length: int = 100, suffixe: str = "...") -> str:
    """
    Tronque un texte à une longueur maximale.

    Args:
        texte: Texte à tronquer.
        max_length: Longueur maximale.
        suffixe: Suffixe à ajouter si tronqué.

    Returns:
        Texte tronqué.
    """
    if not texte or len(texte) <= max_length:
        return texte

    return texte[:max_length - len(suffixe)] + suffixe


def formater_date(date: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formate une date selon le format spécifié.

    Args:
        date: Date à formater (par défaut: maintenant).
        format_str: Format de date.

    Returns:
        Date formatée.
    """
    if date is None:
        date = datetime.now()
    return date.strftime(format_str)


def generer_nom_fichier_rapport(url: str, prefixe: str = "rapport_rgaa") -> str:
    """
    Génère un nom de fichier unique pour un rapport.

    Args:
        url: URL analysée.
        prefixe: Préfixe du nom de fichier.

    Returns:
        Nom de fichier pour le rapport.
    """
    # Extraire le domaine
    domaine = extraire_domaine(url)
    # Nettoyer le domaine pour le nom de fichier
    domaine_clean = re.sub(r'[^a-zA-Z0-9]', '_', domaine)
    # Ajouter la date
    date = formater_date(format_str="%Y%m%d_%H%M%S")

    return f"{prefixe}_{domaine_clean}_{date}.md"


def echapper_html(texte: str) -> str:
    """
    Échappe les caractères spéciaux HTML.

    Args:
        texte: Texte à échapper.

    Returns:
        Texte échappé.
    """
    if not texte:
        return ""

    remplacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }

    for char, escape in remplacements.items():
        texte = texte.replace(char, escape)

    return texte


def echapper_markdown(texte: str) -> str:
    """
    Échappe les caractères spéciaux Markdown.

    Args:
        texte: Texte à échapper.

    Returns:
        Texte échappé pour Markdown.
    """
    if not texte:
        return ""

    # Caractères à échapper dans Markdown
    caracteres = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']

    for char in caracteres:
        texte = texte.replace(char, '\\' + char)

    return texte


def analyser_style_css(style: str) -> dict:
    """
    Parse un attribut style CSS en dictionnaire.

    Args:
        style: Chaîne de style CSS (ex: "display: none; color: red").

    Returns:
        Dictionnaire des propriétés CSS.
    """
    if not style:
        return {}

    result = {}
    # Séparer les déclarations
    declarations = style.split(';')

    for declaration in declarations:
        declaration = declaration.strip()
        if ':' in declaration:
            propriete, valeur = declaration.split(':', 1)
            result[propriete.strip().lower()] = valeur.strip().lower()

    return result


def est_element_cache(style: Optional[str] = None,
                      aria_hidden: Optional[str] = None,
                      hidden: bool = False,
                      width: Optional[str] = None,
                      height: Optional[str] = None) -> Tuple[bool, str]:
    """
    Détermine si un élément est caché (exempté des tests RGAA).

    Args:
        style: Attribut style CSS.
        aria_hidden: Attribut aria-hidden.
        hidden: Attribut hidden présent.
        width: Attribut width.
        height: Attribut height.

    Returns:
        Tuple (est_caché, raison).
    """
    # Vérifier aria-hidden
    if aria_hidden and aria_hidden.lower() == 'true':
        return (True, "aria-hidden=\"true\"")

    # Vérifier attribut hidden
    if hidden:
        return (True, "attribut hidden présent")

    # Vérifier le style CSS
    if style:
        styles = analyser_style_css(style)

        if styles.get('display') == 'none':
            return (True, "display: none")

        if styles.get('visibility') == 'hidden':
            return (True, "visibility: hidden")

    # Vérifier les dimensions nulles
    if width and height:
        try:
            w = int(re.sub(r'[^0-9]', '', width) or '0')
            h = int(re.sub(r'[^0-9]', '', height) or '0')
            if w == 0 and h == 0:
                return (True, "dimensions nulles (width=0, height=0)")
        except ValueError:
            pass

    return (False, "")


def calculer_taux_conformite(conformes: int, non_conformes: int) -> float:
    """
    Calcule le taux de conformité en pourcentage.

    Args:
        conformes: Nombre d'éléments conformes.
        non_conformes: Nombre d'éléments non conformes.

    Returns:
        Taux de conformité (0-100).
    """
    total = conformes + non_conformes
    if total == 0:
        return 100.0  # Pas d'éléments = pas de problème

    return round((conformes / total) * 100, 2)


def formater_taux_conformite(taux: float) -> str:
    """
    Formate un taux de conformité pour affichage.

    Args:
        taux: Taux de conformité.

    Returns:
        Chaîne formatée.
    """
    if taux == 100.0:
        return "100%"
    elif taux == 0.0:
        return "0%"
    else:
        return f"{taux:.1f}%"


def obtenir_statut_conformite(taux: float) -> str:
    """
    Retourne le statut de conformité basé sur le taux.

    Args:
        taux: Taux de conformité.

    Returns:
        Statut ("Conforme", "Non conforme", "Partiellement conforme").
    """
    if taux == 100.0:
        return "Conforme"
    elif taux == 0.0:
        return "Non conforme"
    else:
        return "Partiellement conforme"


def obtenir_emoji_statut(statut: str) -> str:
    """
    Retourne l'emoji correspondant au statut.

    Args:
        statut: Statut de conformité.

    Returns:
        Emoji correspondant.
    """
    emojis = {
        "Conforme": "✅",
        "Non conforme": "❌",
        "Partiellement conforme": "⚠️",
        "Non applicable": "⚪",
        "À vérifier": "🔍"
    }
    return emojis.get(statut, "❓")


def get_system_info() -> Dict[str, str]:
    """
    Récupère les informations sur l'environnement d'exécution.

    Returns:
        dict: Informations système
    """
    info = {
        'os_name': platform.system(),
        'os_version': platform.version(),
        'os_full_info': f"{platform.system()} {platform.release()}",
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'app_version': '1.0.0'
    }

    # Tenter de détecter la version de Selenium
    try:
        from selenium import __version__ as selenium_version
        info['selenium_version'] = selenium_version
    except (ImportError, AttributeError):
        info['selenium_version'] = 'Non disponible'

    # Informations navigateur (à détecter dynamiquement si possible)
    # Pour l'instant, on utilise des valeurs par défaut
    info['browser_name'] = 'Google Chrome'
    info['browser_version'] = 'Dernière version'

    return info
