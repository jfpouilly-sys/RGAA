#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entree GUI tkinter pour le test du critere RGAA 10.7.
Interface coherente avec l'outil rgaa-section2-tester existant.

Usage:
    python test_criterion_10_7.py              # Interface graphique
    python test_criterion_10_7.py --cli URL    # Mode ligne de commande

Critere RGAA 10.7 — Visibilite du focus
WCAG 2.1 SC 2.4.7 Focus Visible (AA)
"""

import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le repertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from criterion_10_7.focus_tester import FocusTester
from criterion_10_7.report_generator import FocusReportGenerator


class FocusTestGUI:
    """Interface graphique pour le test du critere 10.7."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RGAA 10.7 — Test de visibilite du focus")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self._build_ui()
        self._running = False

    def _build_ui(self):
        """Construit l'interface utilisateur."""

        # === Frame superieure : URLs ===
        url_frame = ttk.LabelFrame(
            self.root, text="Pages a tester", padding=10
        )
        url_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(url_frame, text=(
            "Entrez les URLs a tester (une par ligne, format : ID|URL)\n"
            "Exemple : P01|https://www.example.com/"
        )).pack(anchor=tk.W)

        self.url_text = scrolledtext.ScrolledText(
            url_frame, height=8, width=80, font=("Consolas", 10)
        )
        self.url_text.pack(fill=tk.X, pady=5)

        # Boutons import
        btn_frame = ttk.Frame(url_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame, text="Importer depuis fichier",
            command=self._import_urls
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame, text="Coller depuis presse-papiers",
            command=self._paste_urls
        ).pack(side=tk.LEFT, padx=5)

        # === Frame options ===
        options_frame = ttk.LabelFrame(
            self.root, text="Options", padding=10
        )
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        # Nom du site
        site_frame = ttk.Frame(options_frame)
        site_frame.pack(fill=tk.X, pady=2)
        ttk.Label(site_frame, text="Nom du site :").pack(side=tk.LEFT)
        self.site_name_var = tk.StringVar(value="Site audite")
        ttk.Entry(
            site_frame, textvariable=self.site_name_var, width=50
        ).pack(side=tk.LEFT, padx=10)

        # Headless
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Mode headless (sans fenetre navigateur)",
            variable=self.headless_var
        ).pack(anchor=tk.W)

        # Chemin de sortie
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, pady=2)
        ttk.Label(output_frame, text="Dossier de sortie :").pack(
            side=tk.LEFT
        )
        self.output_dir_var = tk.StringVar(
            value=os.path.expanduser("~/rgaa-reports")
        )
        ttk.Entry(
            output_frame, textvariable=self.output_dir_var, width=50
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(
            output_frame, text="...", command=self._browse_output
        ).pack(side=tk.LEFT)

        # === Bouton lancer ===
        self.run_btn = ttk.Button(
            self.root, text="Lancer l'analyse",
            command=self._start_analysis
        )
        self.run_btn.pack(pady=10)

        # === Barre de progression ===
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progress_var,
            maximum=100, mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=10)

        self.status_var = tk.StringVar(value="Pret")
        ttk.Label(
            self.root, textvariable=self.status_var, font=("Arial", 9)
        ).pack(pady=2)

        # === Zone de log ===
        log_frame = ttk.LabelFrame(self.root, text="Journal", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, width=80,
            font=("Consolas", 9), state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _log(self, message: str):
        """Ajoute un message au journal."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _import_urls(self):
        """Importe les URLs depuis un fichier texte."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Fichiers texte", "*.txt"), ("Tous", "*.*")]
        )
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.url_text.delete('1.0', tk.END)
                self.url_text.insert('1.0', f.read())

    def _paste_urls(self):
        """Colle le contenu du presse-papiers."""
        try:
            content = self.root.clipboard_get()
            self.url_text.insert(tk.END, content)
        except tk.TclError:
            pass

    def _browse_output(self):
        """Selectionne le dossier de sortie."""
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def _parse_urls(self) -> list[tuple[str, str]]:
        """Parse les URLs depuis la zone de texte."""
        urls = []
        content = self.url_text.get('1.0', tk.END).strip()
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' in line:
                page_id, url = line.split('|', 1)
                urls.append((url.strip(), page_id.strip()))
            else:
                urls.append((line, f"P{len(urls)+1:02d}"))
        return urls

    def _start_analysis(self):
        """Lance l'analyse dans un thread separe."""
        if self._running:
            return

        urls = self._parse_urls()
        if not urls:
            messagebox.showwarning(
                "Aucune URL",
                "Veuillez entrer au moins une URL."
            )
            return

        self._running = True
        self.run_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)

        thread = threading.Thread(target=self._run_analysis, args=(urls,))
        thread.daemon = True
        thread.start()

    def _run_analysis(self, urls: list[tuple[str, str]]):
        """Execute l'analyse (dans un thread separe)."""
        try:
            self.root.after(
                0, self._log,
                f"Demarrage de l'analyse de {len(urls)} pages..."
            )

            with FocusTester(headless=self.headless_var.get()) as tester:
                results = []

                for i, (url, page_id) in enumerate(urls):
                    def progress_cb(msg, pct, _i=i):
                        overall = (_i + pct) / len(urls) * 100
                        self.root.after(
                            0, self.progress_var.set, overall
                        )
                        self.root.after(
                            0, self.status_var.set,
                            f"{page_id}: {msg}"
                        )
                        self.root.after(0, self._log, f"  {msg}")

                    self.root.after(
                        0, self._log,
                        f"\n{'='*60}"
                    )
                    self.root.after(
                        0, self._log,
                        f"Page {page_id} : {url}"
                    )

                    result = tester.test_page(url, page_id, progress_cb)
                    results.append(result)

                    self.root.after(
                        0, self._log,
                        f"  -> Statut suggere : {result.suggested_status} "
                        f"(confiance: {result.confidence})"
                    )
                    self.root.after(
                        0, self._log,
                        f"  -> {result.total_conforme} C, "
                        f"{result.total_non_conforme} NC, "
                        f"{result.total_a_verifier} a verifier"
                    )

                # Generer le rapport
                output_dir = self.output_dir_var.get()
                os.makedirs(output_dir, exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_path = os.path.join(
                    output_dir,
                    f"rapport_10_7_{timestamp}.md"
                )

                generator = FocusReportGenerator()
                generator.generate(
                    results, report_path,
                    self.site_name_var.get()
                )

                self.root.after(
                    0, self._log, f"\n{'='*60}"
                )
                self.root.after(
                    0, self._log,
                    f"Rapport genere : {report_path}"
                )
                self.root.after(0, self.progress_var.set, 100)
                self.root.after(
                    0, self.status_var.set, "Analyse terminee"
                )

                total_nc = sum(r.total_non_conforme for r in results)
                total_av = sum(r.total_a_verifier for r in results)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Analyse terminee",
                    f"Rapport sauvegarde :\n{report_path}\n\n"
                    f"Pages analysees : {len(results)}\n"
                    f"Total NC : {total_nc}\n"
                    f"Total a verifier : {total_av}"
                ))

        except Exception as e:
            self.root.after(
                0, self._log, f"\nErreur : {str(e)}"
            )
            self.root.after(0, lambda: messagebox.showerror(
                "Erreur", str(e)
            ))

        finally:
            self._running = False
            self.root.after(
                0, lambda: self.run_btn.config(state=tk.NORMAL)
            )


def mode_gui():
    """Lance l'application en mode graphique."""
    root = tk.Tk()
    FocusTestGUI(root)
    root.mainloop()


def mode_cli(urls: list[tuple[str, str]], site_name: str,
             output_dir: str, headless: bool):
    """
    Lance l'analyse en mode ligne de commande.

    Args:
        urls: Liste de tuples (url, page_id)
        site_name: Nom du site audite
        output_dir: Repertoire de sortie
        headless: Mode headless
    """
    print("=" * 60)
    print("RGAA 10.7 — Test de visibilite du focus")
    print("=" * 60)
    print()
    print(f"Pages a analyser : {len(urls)}")
    print()

    with FocusTester(headless=headless) as tester:
        results = []

        for i, (url, page_id) in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {page_id} : {url}")

            def progress_cb(msg, pct):
                print(f"  {msg}")

            result = tester.test_page(url, page_id, progress_cb)
            results.append(result)

            print(
                f"  -> Statut : {result.suggested_status} "
                f"(confiance: {result.confidence})"
            )
            print(
                f"  -> C={result.total_conforme}, "
                f"NC={result.total_non_conforme}, "
                f"A verifier={result.total_a_verifier}"
            )
            print()

    # Generer le rapport
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(
        output_dir, f"rapport_10_7_{timestamp}.md"
    )

    generator = FocusReportGenerator()
    generator.generate(results, report_path, site_name)

    print("=" * 60)
    print("SYNTHESE")
    print("=" * 60)
    total_c = sum(r.total_conforme for r in results)
    total_nc = sum(r.total_non_conforme for r in results)
    total_av = sum(r.total_a_verifier for r in results)
    total_el = sum(r.total_visible for r in results)
    print(f"  Elements analyses  : {total_el}")
    print(f"  Conformes          : {total_c}")
    print(f"  Non conformes      : {total_nc}")
    print(f"  A verifier         : {total_av}")
    print()
    print(f"Rapport genere : {report_path}")
    print()
    print("Termine.")


def main():
    """Point d'entree principal."""
    parser = argparse.ArgumentParser(
        description=(
            "RGAA 10.7 — Test de visibilite du focus"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python test_criterion_10_7.py
  python test_criterion_10_7.py --cli "P01|https://www.example.com/"
  python test_criterion_10_7.py --cli "P01|https://example.com/" "P02|https://example.com/about"
  python test_criterion_10_7.py --cli "https://example.com/" --site "Mon Site"
"""
    )

    parser.add_argument(
        '--cli',
        nargs='+',
        metavar='URL',
        help=(
            "Mode ligne de commande. URLs au format ID|URL "
            "ou URL seule"
        )
    )

    parser.add_argument(
        '--site',
        default="Site audite",
        help="Nom du site audite (defaut: Site audite)"
    )

    parser.add_argument(
        '--output', '-o',
        default=os.path.expanduser("~/rgaa-reports"),
        help="Repertoire de sortie (defaut: ~/rgaa-reports)"
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help="Afficher le navigateur pendant l'analyse"
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='RGAA 10.7 Focus Tester v1.0.0'
    )

    args = parser.parse_args()

    if args.cli:
        # Parser les URLs
        urls = []
        for entry in args.cli:
            entry = entry.strip()
            if '|' in entry:
                page_id, url = entry.split('|', 1)
                urls.append((url.strip(), page_id.strip()))
            else:
                urls.append((entry, f"P{len(urls)+1:02d}"))

        mode_cli(urls, args.site, args.output, not args.no_headless)
    else:
        mode_gui()


if __name__ == "__main__":
    main()
