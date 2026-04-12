# -*- coding: utf-8 -*-
"""
Module de crawling pour RGAA Section 2 Tester

Permet de parcourir un site web et de collecter les pages à analyser.
"""

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import get_config
from .utils import normaliser_url, est_url_valide, est_meme_domaine


@dataclass
class PageCrawlee:
    """Informations sur une page crawlée."""
    url: str
    html: str
    statut_http: int
    erreur: Optional[str] = None
    temps_reponse: float = 0.0


@dataclass
class StatistiqueCrawl:
    """Statistiques du processus de crawl."""
    pages_trouvees: int = 0
    pages_crawlees: int = 0
    pages_erreur: int = 0
    temps_total: float = 0.0


class Crawler:
    """
    Crawler web pour collecter les pages d'un site.

    Parcourt un site en suivant les liens internes et collecte
    le contenu HTML de chaque page pour analyse.
    """

    def __init__(self, config=None):
        """
        Initialise le crawler.

        Args:
            config: Instance de configuration (optionnel).
        """
        self.config = config or get_config()
        crawler_config = self.config.crawler_config

        self._max_pages = crawler_config.get('max_pages', 50)
        self._timeout = crawler_config.get('timeout', 30)
        self._user_agent = crawler_config.get('user_agent', 'RGAA-Tester/1.0')
        self._delai = crawler_config.get('delai_entre_requetes', 1.0)
        self._suivre_externe = crawler_config.get('suivre_liens_externes', False)

        # État du crawl
        self._urls_visitees: Set[str] = set()
        self._urls_a_visiter: List[str] = []
        self._pages_collectees: List[PageCrawlee] = []
        self._statistiques = StatistiqueCrawl()

        # Callbacks pour mise à jour de l'interface
        self._callback_progression: Optional[Callable[[int, int, str], None]] = None
        self._callback_log: Optional[Callable[[str], None]] = None

        # Contrôle d'arrêt
        self._arreter = False

    def definir_callback_progression(self, callback: Callable[[int, int, str], None]) -> None:
        """
        Définit le callback de progression.

        Args:
            callback: Fonction(pages_crawlees, total_estimé, message)
        """
        self._callback_progression = callback

    def definir_callback_log(self, callback: Callable[[str], None]) -> None:
        """
        Définit le callback de log.

        Args:
            callback: Fonction(message)
        """
        self._callback_log = callback

    def arreter(self) -> None:
        """Demande l'arrêt du crawl."""
        self._arreter = True

    def reinitialiser(self) -> None:
        """Réinitialise l'état du crawler."""
        self._urls_visitees.clear()
        self._urls_a_visiter.clear()
        self._pages_collectees.clear()
        self._statistiques = StatistiqueCrawl()
        self._arreter = False

    def _log(self, message: str) -> None:
        """Envoie un message de log."""
        if self._callback_log:
            self._callback_log(message)

    def _progression(self, pages: int, total: int, message: str) -> None:
        """Met à jour la progression."""
        if self._callback_progression:
            self._callback_progression(pages, total, message)

    def crawl(self, url_depart: str, max_pages: Optional[int] = None) -> List[PageCrawlee]:
        """
        Lance le crawl à partir d'une URL de départ.

        Args:
            url_depart: URL de départ du crawl.
            max_pages: Nombre maximum de pages à crawler (optionnel).

        Returns:
            Liste des pages crawlées.
        """
        self.reinitialiser()
        debut = time.time()

        if max_pages is not None:
            self._max_pages = max_pages

        # Normaliser l'URL de départ
        url_depart = normaliser_url(url_depart)
        if not est_url_valide(url_depart):
            self._log(f"Erreur : URL invalide : {url_depart}")
            return []

        self._urls_a_visiter.append(url_depart)
        self._domaine_principal = urlparse(url_depart).netloc

        self._log(f"Démarrage du crawl sur : {url_depart}")
        self._log(f"Maximum de pages : {self._max_pages}")

        while self._urls_a_visiter and not self._arreter:
            if len(self._pages_collectees) >= self._max_pages:
                self._log(f"Limite de {self._max_pages} pages atteinte.")
                break

            url = self._urls_a_visiter.pop(0)
            url_normalisee = normaliser_url(url)

            if url_normalisee in self._urls_visitees:
                continue

            self._urls_visitees.add(url_normalisee)
            self._progression(
                len(self._pages_collectees),
                min(len(self._urls_a_visiter) + len(self._pages_collectees) + 1, self._max_pages),
                f"Analyse de : {url_normalisee[:50]}..."
            )

            page = self._recuperer_page(url_normalisee)
            if page:
                self._pages_collectees.append(page)
                self._statistiques.pages_crawlees += 1

                # Extraire les liens de la page
                if page.html:
                    self._extraire_liens(page.html, url_normalisee)
            else:
                self._statistiques.pages_erreur += 1

            # Respecter le délai entre les requêtes
            if self._delai > 0 and self._urls_a_visiter:
                time.sleep(self._delai)

        self._statistiques.temps_total = time.time() - debut
        self._statistiques.pages_trouvees = len(self._urls_visitees)

        self._log(f"Crawl terminé. {len(self._pages_collectees)} pages analysées en {self._statistiques.temps_total:.1f}s")

        return self._pages_collectees

    def crawl_page_unique(self, url: str) -> Optional[PageCrawlee]:
        """
        Crawl une seule page sans suivre les liens.

        Args:
            url: URL de la page à crawler.

        Returns:
            Page crawlée ou None en cas d'erreur.
        """
        url = normaliser_url(url)
        if not est_url_valide(url):
            self._log(f"Erreur : URL invalide : {url}")
            return None

        self._log(f"Récupération de la page : {url}")
        return self._recuperer_page(url)

    def _recuperer_page(self, url: str) -> Optional[PageCrawlee]:
        """
        Récupère le contenu HTML d'une URL.

        Args:
            url: URL à récupérer.

        Returns:
            PageCrawlee ou None en cas d'erreur.
        """
        headers = {
            'User-Agent': self._user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }

        try:
            debut = time.time()
            response = requests.get(
                url,
                headers=headers,
                timeout=self._timeout,
                allow_redirects=True
            )
            temps_reponse = time.time() - debut

            # Vérifier le type de contenu
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                self._log(f"Ignoré (non-HTML) : {url}")
                return None

            response.encoding = response.apparent_encoding or 'utf-8'

            return PageCrawlee(
                url=url,
                html=response.text,
                statut_http=response.status_code,
                temps_reponse=temps_reponse
            )

        except requests.Timeout:
            self._log(f"Timeout : {url}")
            return PageCrawlee(url=url, html="", statut_http=0, erreur="Timeout")

        except requests.RequestException as e:
            self._log(f"Erreur de requête : {url} - {str(e)}")
            return PageCrawlee(url=url, html="", statut_http=0, erreur=str(e))

        except Exception as e:
            self._log(f"Erreur inattendue : {url} - {str(e)}")
            return PageCrawlee(url=url, html="", statut_http=0, erreur=str(e))

    def _extraire_liens(self, html: str, url_base: str) -> None:
        """
        Extrait les liens d'une page HTML.

        Args:
            html: Contenu HTML de la page.
            url_base: URL de base pour résoudre les liens relatifs.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            for lien in soup.find_all('a', href=True):
                href = lien['href']

                # Ignorer les liens non-HTTP
                if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue

                # Construire l'URL absolue
                url_absolue = urljoin(url_base, href)
                url_normalisee = normaliser_url(url_absolue)

                # Vérifier la validité
                if not est_url_valide(url_normalisee):
                    continue

                # Vérifier si c'est le même domaine
                if not self._suivre_externe:
                    if urlparse(url_normalisee).netloc != self._domaine_principal:
                        continue

                # Ignorer les fichiers non-HTML
                extensions_ignorees = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
                                       '.css', '.js', '.ico', '.xml', '.json', '.zip',
                                       '.doc', '.docx', '.xls', '.xlsx', '.mp3', '.mp4')
                if any(url_normalisee.lower().endswith(ext) for ext in extensions_ignorees):
                    continue

                # Ajouter si pas encore visité
                if url_normalisee not in self._urls_visitees:
                    if url_normalisee not in self._urls_a_visiter:
                        self._urls_a_visiter.append(url_normalisee)

        except Exception as e:
            self._log(f"Erreur lors de l'extraction des liens : {str(e)}")

    @property
    def statistiques(self) -> StatistiqueCrawl:
        """Retourne les statistiques du crawl."""
        return self._statistiques

    @property
    def pages_collectees(self) -> List[PageCrawlee]:
        """Retourne les pages collectées."""
        return self._pages_collectees
