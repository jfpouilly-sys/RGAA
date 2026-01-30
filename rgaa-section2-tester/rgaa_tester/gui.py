# -*- coding: utf-8 -*-
"""
Module d'interface graphique pour RGAA Section 2 Tester

Interface utilisateur tkinter pour l'analyse RGAA et la génération de rapports.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
from pathlib import Path
from typing import Optional

from .analyzer import AnalyseurRGAA, ResultatAnalyseGlobal, ResultatPage
from .config import get_config
from .crawler import Crawler, PageCrawlee
from .report_generator import GenerateurRapport
from .utils import est_url_valide, formater_date, normaliser_url


class ApplicationRGAA(tk.Tk):
    """
    Application principale RGAA Section 2 Tester.

    Interface graphique complète pour l'analyse de conformité RGAA
    et la génération de rapports Markdown.
    """

    def __init__(self):
        """Initialise l'application."""
        super().__init__()

        # Configuration
        self.config = get_config()

        # Composants
        self.crawler = Crawler(self.config)
        self.analyseur = AnalyseurRGAA(self.config)
        self.generateur = GenerateurRapport(self.config)

        # État
        self._analyse_en_cours = False
        self._thread_analyse: Optional[threading.Thread] = None
        self._resultat_global: Optional[ResultatAnalyseGlobal] = None

        # Configuration de la fenêtre
        self._configurer_fenetre()
        self._creer_interface()

    def _configurer_fenetre(self) -> None:
        """Configure les propriétés de la fenêtre principale."""
        self.title("RGAA Section 2 Tester - Analyse des Cadres (Frames)")

        # Dimensions
        largeur = self.config.get("gui.largeur_fenetre", 900)
        hauteur = self.config.get("gui.hauteur_fenetre", 700)

        # Centrer la fenêtre
        ecran_l = self.winfo_screenwidth()
        ecran_h = self.winfo_screenheight()
        x = (ecran_l - largeur) // 2
        y = (ecran_h - hauteur) // 2

        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")
        self.minsize(800, 600)

        # Icône (si disponible)
        # self.iconbitmap('icon.ico')

    def _creer_interface(self) -> None:
        """Crée les éléments de l'interface utilisateur."""
        # Conteneur principal avec padding
        self.conteneur = ttk.Frame(self, padding="10")
        self.conteneur.pack(fill=tk.BOTH, expand=True)

        # Sections de l'interface
        self._creer_section_entete()
        self._creer_section_configuration()
        self._creer_section_actions()
        self._creer_section_progression()
        self._creer_section_logs()
        self._creer_section_resultats()
        self._creer_barre_statut()

    def _creer_section_entete(self) -> None:
        """Crée l'en-tête de l'application."""
        frame = ttk.Frame(self.conteneur)
        frame.pack(fill=tk.X, pady=(0, 10))

        titre = ttk.Label(
            frame,
            text="RGAA 4.1.2 - Section 2 : Cadres (Frames)",
            font=('Helvetica', 16, 'bold')
        )
        titre.pack()

        sous_titre = ttk.Label(
            frame,
            text="Testeur de conformité accessibilité pour les éléments iframe et frame",
            font=('Helvetica', 10)
        )
        sous_titre.pack()

    def _creer_section_configuration(self) -> None:
        """Crée la section de configuration."""
        frame = ttk.LabelFrame(self.conteneur, text="Configuration", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # URL
        frame_url = ttk.Frame(frame)
        frame_url.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame_url, text="URL à analyser :").pack(side=tk.LEFT)
        self.entree_url = ttk.Entry(frame_url, width=60)
        self.entree_url.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.entree_url.insert(0, "https://")
        self.entree_url.bind('<Return>', lambda e: self._lancer_analyse())

        # Options
        frame_options = ttk.Frame(frame)
        frame_options.pack(fill=tk.X, pady=(5, 0))

        # Mode d'analyse
        ttk.Label(frame_options, text="Mode :").pack(side=tk.LEFT)

        self.var_mode = tk.StringVar(value="unique")
        ttk.Radiobutton(
            frame_options, text="Page unique",
            variable=self.var_mode, value="unique"
        ).pack(side=tk.LEFT, padx=(10, 5))

        ttk.Radiobutton(
            frame_options, text="Crawler multi-pages",
            variable=self.var_mode, value="crawler"
        ).pack(side=tk.LEFT, padx=(5, 20))

        # Nombre max de pages
        ttk.Label(frame_options, text="Max pages :").pack(side=tk.LEFT)
        self.spin_max_pages = ttk.Spinbox(
            frame_options, from_=1, to=100, width=5,
            state="readonly"
        )
        self.spin_max_pages.set(10)
        self.spin_max_pages.pack(side=tk.LEFT, padx=(5, 0))

    def _creer_section_actions(self) -> None:
        """Crée la section des boutons d'action."""
        frame = ttk.Frame(self.conteneur)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_analyser = ttk.Button(
            frame, text="Lancer l'analyse",
            command=self._lancer_analyse,
            style='Accent.TButton'
        )
        self.btn_analyser.pack(side=tk.LEFT)

        self.btn_arreter = ttk.Button(
            frame, text="Arrêter",
            command=self._arreter_analyse,
            state=tk.DISABLED
        )
        self.btn_arreter.pack(side=tk.LEFT, padx=(10, 0))

        self.btn_rapport = ttk.Button(
            frame, text="Générer le rapport",
            command=self._generer_rapport,
            state=tk.DISABLED
        )
        self.btn_rapport.pack(side=tk.LEFT, padx=(10, 0))

        self.btn_ouvrir_rapport = ttk.Button(
            frame, text="Ouvrir le dernier rapport",
            command=self._ouvrir_dernier_rapport,
            state=tk.DISABLED
        )
        self.btn_ouvrir_rapport.pack(side=tk.LEFT, padx=(10, 0))

        # Bouton effacer à droite
        self.btn_effacer = ttk.Button(
            frame, text="Effacer",
            command=self._effacer_tout
        )
        self.btn_effacer.pack(side=tk.RIGHT)

    def _creer_section_progression(self) -> None:
        """Crée la section de progression."""
        frame = ttk.Frame(self.conteneur)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.label_progression = ttk.Label(frame, text="En attente...")
        self.label_progression.pack(fill=tk.X)

        self.barre_progression = ttk.Progressbar(
            frame, mode='determinate', length=400
        )
        self.barre_progression.pack(fill=tk.X, pady=(5, 0))

    def _creer_section_logs(self) -> None:
        """Crée la section des logs."""
        frame = ttk.LabelFrame(self.conteneur, text="Journal d'activité", padding="5")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.zone_logs = scrolledtext.ScrolledText(
            frame, height=10, wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.zone_logs.pack(fill=tk.BOTH, expand=True)
        self.zone_logs.config(state=tk.DISABLED)

    def _creer_section_resultats(self) -> None:
        """Crée la section des résultats."""
        frame = ttk.LabelFrame(self.conteneur, text="Résultats", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Grille de résultats
        self.frame_resultats = ttk.Frame(frame)
        self.frame_resultats.pack(fill=tk.X)

        # Labels pour les statistiques
        self._creer_label_stat("Pages analysées :", "0", 0, 0)
        self._creer_label_stat("Cadres détectés :", "0", 0, 1)
        self._creer_label_stat("Cadres testés :", "0", 0, 2)

        self._creer_label_stat("Critère 2.1 - Conformes :", "0", 1, 0)
        self._creer_label_stat("Critère 2.1 - Non conformes :", "0", 1, 1)
        self._creer_label_stat("Taux de conformité :", "- %", 1, 2)

        self._creer_label_stat("Critère 2.2 - À vérifier :", "0", 2, 0)
        self._creer_label_stat("Alertes détectées :", "0", 2, 1)
        self._creer_label_stat("Statut global :", "-", 2, 2)

    def _creer_label_stat(self, label: str, valeur: str, row: int, col: int) -> None:
        """Crée un label de statistique."""
        frame = ttk.Frame(self.frame_resultats)
        frame.grid(row=row, column=col, padx=10, pady=2, sticky='w')

        ttk.Label(frame, text=label, font=('Helvetica', 9)).pack(side=tk.LEFT)
        label_val = ttk.Label(frame, text=valeur, font=('Helvetica', 9, 'bold'))
        label_val.pack(side=tk.LEFT, padx=(5, 0))

        # Stocker la référence au label de valeur
        nom_attr = f"stat_{row}_{col}"
        setattr(self, nom_attr, label_val)

    def _creer_barre_statut(self) -> None:
        """Crée la barre de statut."""
        self.barre_statut = ttk.Label(
            self.conteneur,
            text="Prêt",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.barre_statut.pack(fill=tk.X, side=tk.BOTTOM)

    def _log(self, message: str) -> None:
        """
        Ajoute un message au journal.

        Args:
            message: Message à ajouter.
        """
        horodatage = formater_date(format_str="%H:%M:%S")
        ligne = f"[{horodatage}] {message}\n"

        self.zone_logs.config(state=tk.NORMAL)
        self.zone_logs.insert(tk.END, ligne)
        self.zone_logs.see(tk.END)
        self.zone_logs.config(state=tk.DISABLED)

    def _mettre_a_jour_progression(self, pages: int, total: int, message: str) -> None:
        """Met à jour la barre de progression."""
        self.label_progression.config(text=message)

        if total > 0:
            pourcentage = (pages / total) * 100
            self.barre_progression['value'] = pourcentage

    def _mettre_a_jour_statistiques(self, resultat: ResultatAnalyseGlobal) -> None:
        """Met à jour les statistiques affichées."""
        self.stat_0_0.config(text=str(resultat.total_pages))
        self.stat_0_1.config(text=str(resultat.total_cadres))
        self.stat_0_2.config(text=str(resultat.total_cadres_testes))

        self.stat_1_0.config(text=str(resultat.total_conformes_2_1))
        self.stat_1_1.config(text=str(resultat.total_non_conformes_2_1))

        taux = f"{resultat.taux_conformite_2_1:.1f}%"
        self.stat_1_2.config(text=taux)

        self.stat_2_0.config(text=str(resultat.total_a_verifier_2_2))
        self.stat_2_1.config(text=str(resultat.total_alertes_2_2))
        self.stat_2_2.config(text=resultat.statut_section_2)

    def _lancer_analyse(self) -> None:
        """Lance l'analyse RGAA."""
        url = self.entree_url.get().strip()

        if not url or url == "https://":
            messagebox.showwarning("URL requise", "Veuillez entrer une URL à analyser.")
            return

        # Normaliser l'URL
        url = normaliser_url(url)

        if not est_url_valide(url):
            messagebox.showerror("URL invalide", "L'URL entrée n'est pas valide.")
            return

        # Désactiver les contrôles
        self._analyse_en_cours = True
        self.btn_analyser.config(state=tk.DISABLED)
        self.btn_arreter.config(state=tk.NORMAL)
        self.btn_rapport.config(state=tk.DISABLED)
        self.entree_url.config(state=tk.DISABLED)

        # Réinitialiser la progression
        self.barre_progression['value'] = 0
        self.label_progression.config(text="Démarrage de l'analyse...")
        self.barre_statut.config(text="Analyse en cours...")

        self._log(f"Démarrage de l'analyse de : {url}")

        # Lancer l'analyse dans un thread séparé
        mode = self.var_mode.get()
        max_pages = int(self.spin_max_pages.get()) if mode == "crawler" else 1

        self._thread_analyse = threading.Thread(
            target=self._executer_analyse,
            args=(url, mode, max_pages),
            daemon=True
        )
        self._thread_analyse.start()

    def _executer_analyse(self, url: str, mode: str, max_pages: int) -> None:
        """
        Exécute l'analyse dans un thread séparé.

        Args:
            url: URL à analyser.
            mode: Mode d'analyse ('unique' ou 'crawler').
            max_pages: Nombre maximum de pages.
        """
        try:
            # Configurer les callbacks du crawler
            self.crawler.definir_callback_log(
                lambda msg: self.after(0, lambda: self._log(msg))
            )
            self.crawler.definir_callback_progression(
                lambda p, t, m: self.after(0, lambda: self._mettre_a_jour_progression(p, t, m))
            )

            # Récupérer les pages
            if mode == "unique":
                self._log("Mode : Page unique")
                page = self.crawler.crawl_page_unique(url)
                pages = [page] if page and page.html else []
            else:
                self._log(f"Mode : Crawler multi-pages (max {max_pages})")
                pages = self.crawler.crawl(url, max_pages)

            if not pages:
                self.after(0, lambda: self._terminer_analyse(None, "Aucune page récupérée."))
                return

            # Analyser les pages
            self._log(f"Analyse de {len(pages)} page(s)...")
            self._resultat_global = ResultatAnalyseGlobal(
                url_depart=url,
                date_analyse=formater_date()
            )

            for i, page in enumerate(pages):
                if not self._analyse_en_cours:
                    break

                self.after(0, lambda i=i, t=len(pages): self._mettre_a_jour_progression(
                    i + 1, t, f"Analyse de la page {i + 1}/{t}..."
                ))

                if page.html:
                    resultat_page = self.analyseur.analyser_page(page.html, page.url)
                    self._resultat_global.pages.append(resultat_page)

                    self._log(f"Page analysée : {page.url[:50]}... - {resultat_page.cadres_testes} cadre(s)")

            # Calculer les statistiques finales
            self._resultat_global.calculer_statistiques()

            self.after(0, lambda: self._terminer_analyse(
                self._resultat_global,
                f"Analyse terminée : {self._resultat_global.total_pages} page(s), "
                f"{self._resultat_global.total_cadres} cadre(s)"
            ))

        except Exception as e:
            self.after(0, lambda: self._terminer_analyse(None, f"Erreur : {str(e)}"))

    def _terminer_analyse(self, resultat: Optional[ResultatAnalyseGlobal], message: str) -> None:
        """
        Termine l'analyse et met à jour l'interface.

        Args:
            resultat: Résultat de l'analyse (ou None en cas d'erreur).
            message: Message de fin.
        """
        self._analyse_en_cours = False

        # Réactiver les contrôles
        self.btn_analyser.config(state=tk.NORMAL)
        self.btn_arreter.config(state=tk.DISABLED)
        self.entree_url.config(state=tk.NORMAL)

        self._log(message)
        self.label_progression.config(text=message)
        self.barre_progression['value'] = 100 if resultat else 0

        if resultat:
            self._mettre_a_jour_statistiques(resultat)
            self.btn_rapport.config(state=tk.NORMAL)
            self.barre_statut.config(text="Analyse terminée - Rapport disponible")
        else:
            self.barre_statut.config(text="Analyse échouée")

    def _arreter_analyse(self) -> None:
        """Arrête l'analyse en cours."""
        self._analyse_en_cours = False
        self.crawler.arreter()
        self._log("Arrêt de l'analyse demandé...")
        self.btn_arreter.config(state=tk.DISABLED)

    def _generer_rapport(self) -> None:
        """Génère le rapport Markdown."""
        if not self._resultat_global:
            messagebox.showwarning("Pas de données", "Aucune analyse disponible.")
            return

        # Demander où sauvegarder
        chemin = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Fichiers Markdown", "*.md"), ("Tous les fichiers", "*.*")],
            initialfile=f"rapport_rgaa_{formater_date(format_str='%Y%m%d_%H%M%S')}.md"
        )

        if not chemin:
            return

        try:
            chemin_rapport = self.generateur.generer_rapport(
                self._resultat_global,
                chemin
            )
            self._log(f"Rapport généré : {chemin_rapport}")
            self.barre_statut.config(text=f"Rapport sauvegardé : {chemin_rapport}")
            self.btn_ouvrir_rapport.config(state=tk.NORMAL)
            self._dernier_rapport = chemin_rapport

            messagebox.showinfo(
                "Rapport généré",
                f"Le rapport a été sauvegardé :\n{chemin_rapport}"
            )

        except Exception as e:
            self._log(f"Erreur lors de la génération du rapport : {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de générer le rapport :\n{str(e)}")

    def _ouvrir_dernier_rapport(self) -> None:
        """Ouvre le dernier rapport généré."""
        if hasattr(self, '_dernier_rapport') and os.path.exists(self._dernier_rapport):
            import subprocess
            import platform

            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self._dernier_rapport])
            elif platform.system() == 'Windows':
                os.startfile(self._dernier_rapport)
            else:  # Linux
                subprocess.run(['xdg-open', self._dernier_rapport])
        else:
            messagebox.showwarning("Pas de rapport", "Aucun rapport disponible.")

    def _effacer_tout(self) -> None:
        """Efface tous les résultats et logs."""
        self.zone_logs.config(state=tk.NORMAL)
        self.zone_logs.delete(1.0, tk.END)
        self.zone_logs.config(state=tk.DISABLED)

        self.barre_progression['value'] = 0
        self.label_progression.config(text="En attente...")

        # Réinitialiser les statistiques
        for row in range(3):
            for col in range(3):
                label = getattr(self, f"stat_{row}_{col}", None)
                if label:
                    if col == 2 and row == 1:
                        label.config(text="- %")
                    elif col == 2 and row == 2:
                        label.config(text="-")
                    else:
                        label.config(text="0")

        self._resultat_global = None
        self.btn_rapport.config(state=tk.DISABLED)
        self.btn_ouvrir_rapport.config(state=tk.DISABLED)
        self.barre_statut.config(text="Prêt")

        self._log("Interface réinitialisée.")


def lancer_application() -> None:
    """Lance l'application RGAA Tester."""
    app = ApplicationRGAA()
    app.mainloop()
