# -*- coding: utf-8 -*-
"""
GUI components for ODS-based RGAA audit analysis.

Provides Tkinter interface for working with grilleAudit.ods files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .ods_handler import RGAAAuditODSHandler
from .ods_analyzer import ODSAuditAnalyzer
from .ods_models import Status, Derogation
from .config import get_config


class ODSAuditFrame(ttk.Frame):
    """Frame for ODS-based audit analysis."""

    def __init__(self, parent):
        """
        Initialize the ODS audit frame.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.audit_handler = None
        self.audit_analyzer = None
        self.audit_data = None
        self.config = get_config()
        self._log_file = None  # File handle for auto-save log
        self._log_file_path = None

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # File selection section
        self._create_file_section()

        # Audit information section
        self._create_info_section()

        # Pages list section
        self._create_pages_section()

        # Options section (parallel analysis)
        self._create_options_section()

        # Action buttons section
        self._create_actions_section()

        # Log output section
        self._create_log_section()

    def _create_file_section(self):
        """Create file selection section."""
        file_frame = ttk.LabelFrame(self, text="📁 Fichier d'audit ODS", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        # File path entry
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill="x")

        self.file_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.file_path_var, width=60).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(path_frame, text="Parcourir...", command=self.browse_file).pack(side="left", padx=2)
        ttk.Button(path_frame, text="Charger", command=self.load_file).pack(side="left", padx=2)

        # Output directory section
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(output_frame, text="📂 Répertoire de sortie (logs, CSV, stats):").pack(side="left")

        output_path_frame = ttk.Frame(file_frame)
        output_path_frame.pack(fill="x", pady=(5, 0))

        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set("")  # Empty = use ODS directory
        ttk.Entry(output_path_frame, textvariable=self.output_dir_var, width=60).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(output_path_frame, text="Parcourir...", command=self.browse_output_dir).pack(side="left", padx=2)
        ttk.Button(output_path_frame, text="Réinitialiser", command=self._reset_output_dir).pack(side="left", padx=2)

        # Help text
        ttk.Label(file_frame, text="(Vide = même répertoire que le fichier ODS)", foreground="gray").pack(anchor="w", pady=(2, 0))

    def _create_info_section(self):
        """Create audit information section."""
        info_frame = ttk.LabelFrame(self, text="ℹ️ Informations de l'audit", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        # Create grid for info display
        self.info_labels = {}
        labels = [
            ("Date", "date"),
            ("Auditeur", "auditor"),
            ("Contexte", "context"),
            ("Site", "site")
        ]

        for i, (label, key) in enumerate(labels):
            ttk.Label(info_frame, text=f"{label}:", font=("", 9, "bold")).grid(row=i, column=0, sticky="e", padx=(0, 10), pady=2)
            value_label = ttk.Label(info_frame, text="-", font=("", 9))
            value_label.grid(row=i, column=1, sticky="w", pady=2)
            self.info_labels[key] = value_label

    def _create_pages_section(self):
        """Create pages list section."""
        pages_frame = ttk.LabelFrame(self, text="📄 Pages à auditer", padding=10)
        pages_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create treeview with scrollbar
        tree_container = ttk.Frame(pages_frame)
        tree_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side="right", fill="y")

        self.pages_tree = ttk.Treeview(
            tree_container,
            columns=("id", "title", "url", "status"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.pages_tree.yview)

        # Configure columns
        self.pages_tree.heading("id", text="N°")
        self.pages_tree.heading("title", text="Titre de la page")
        self.pages_tree.heading("url", text="URL")
        self.pages_tree.heading("status", text="Statut")

        self.pages_tree.column("id", width=50, anchor="center")
        self.pages_tree.column("title", width=200)
        self.pages_tree.column("url", width=300)
        self.pages_tree.column("status", width=100, anchor="center")

        # Configure tags for row colors
        self.pages_tree.tag_configure("checked", background="#cce5ff", foreground="#004085")  # Blue for checked pages
        self.pages_tree.tag_configure("not_checked", background="white", foreground="black")  # Default

        self.pages_tree.pack(fill="both", expand=True)

        # Add context menu
        self.pages_tree.bind("<Double-1>", lambda e: self.analyze_selected_page())

    def _create_options_section(self):
        """Create options section for parallel analysis."""
        options_frame = ttk.LabelFrame(self, text="⚙️ Options d'analyse", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Parallel analysis checkbox
        self.parallel_enabled = tk.BooleanVar(value=False)
        parallel_check = ttk.Checkbutton(
            options_frame,
            text="Analyse parallèle",
            variable=self.parallel_enabled
        )
        parallel_check.pack(side="left", padx=5)

        # Number of workers
        ttk.Label(options_frame, text="Nombre de threads:").pack(side="left", padx=(20, 5))
        self.parallel_workers = tk.IntVar(value=4)
        workers_spinbox = ttk.Spinbox(
            options_frame,
            from_=2,
            to=16,
            width=5,
            textvariable=self.parallel_workers
        )
        workers_spinbox.pack(side="left", padx=5)

        # Info label
        ttk.Label(
            options_frame,
            text="(Recommandé: 4-8 pour machines puissantes)",
            foreground="gray"
        ).pack(side="left", padx=10)

    def _create_actions_section(self):
        """Create action buttons section."""
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            action_frame,
            text="🔍 Analyser page sélectionnée",
            command=self.analyze_selected_page
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame,
            text="🔍 Analyser toutes les pages",
            command=self.analyze_all_pages
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame,
            text="💾 Enregistrer résultats",
            command=self.save_results
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame,
            text="📊 Voir statistiques",
            command=self.show_statistics
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame,
            text="📋 Voir journal",
            command=self.view_log
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame,
            text="🔄 Réinitialiser statuts",
            command=self.clear_status
        ).pack(side="left", padx=5)

    def _create_log_section(self):
        """Create log output section."""
        log_frame = ttk.LabelFrame(self, text="📝 Journal", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            state="disabled",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True)

    def browse_file(self):
        """Open file browser to select ODS file."""
        filepath = filedialog.askopenfilename(
            title="Sélectionner le fichier d'audit RGAA",
            filetypes=[
                ("OpenDocument Spreadsheet", "*.ods"),
                ("All files", "*.*")
            ],
            initialdir=str(Path.home())
        )
        if filepath:
            self.file_path_var.set(filepath)

    def browse_output_dir(self):
        """Open directory browser to select output directory."""
        import os
        # Start from current output dir or ODS dir
        initial_dir = self.output_dir_var.get()
        if not initial_dir:
            ods_path = self.file_path_var.get()
            if ods_path:
                initial_dir = os.path.dirname(ods_path)
            else:
                initial_dir = str(Path.home())

        directory = filedialog.askdirectory(
            title="Sélectionner le répertoire de sortie",
            initialdir=initial_dir
        )
        if directory:
            self.output_dir_var.set(directory)
            self.log(f"📂 Répertoire de sortie: {directory}")

    def _reset_output_dir(self):
        """Reset output directory to use ODS file directory."""
        self.output_dir_var.set("")
        self.log("📂 Répertoire de sortie réinitialisé (utilise le répertoire du fichier ODS)")

    def _get_output_dir(self) -> str:
        """
        Get the output directory for saving files.

        Returns:
            Output directory path (uses ODS directory if not specified)
        """
        import os
        output_dir = self.output_dir_var.get().strip()
        if output_dir:
            # Create directory if it doesn't exist
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    self.log(f"⚠️ Impossible de créer le répertoire: {e}")
                    # Fall back to ODS directory
                    output_dir = ""

        if not output_dir:
            # Use ODS file directory
            ods_path = self.file_path_var.get()
            output_dir = os.path.dirname(ods_path) if ods_path else "."

        return output_dir or "."

    def load_file(self):
        """Load the ODS file and display audit information."""
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier ODS")
            return

        self.log("Chargement du fichier d'audit...")
        self.log("⏳ Veuillez patienter...")

        # Run loading in background thread to keep GUI responsive
        thread = threading.Thread(
            target=self._load_file_thread,
            args=(filepath,),
            daemon=True
        )
        thread.start()

    def _load_file_thread(self, filepath: str):
        """Load file in background thread."""
        try:
            self.audit_handler = RGAAAuditODSHandler(filepath)
            self.audit_data = self.audit_handler.load()
            self.audit_analyzer = ODSAuditAnalyzer(self.audit_handler, self.config)

            # Update UI on main thread
            self.after(0, self._load_file_complete)

        except Exception as e:
            self.after(0, lambda: self._load_file_error(str(e)))

    def _update_analyzer_output_dir(self):
        """Update the analyzer's output directory before analysis."""
        if self.audit_analyzer:
            self.audit_analyzer.output_dir = self._get_output_dir()

    def _load_file_complete(self):
        """Called when file loading completes successfully."""
        # Update info labels
        self.info_labels['date'].config(text=self.audit_data.date or "-")
        self.info_labels['auditor'].config(text=self.audit_data.auditor or "-")
        self.info_labels['context'].config(text=self.audit_data.context or "-")
        self.info_labels['site'].config(text=self.audit_data.site_url or "-")

        # Open log file in the same directory as the ODS file
        self._open_log_file()

        # Populate pages list
        self.populate_pages_list()

        self.log(f"✅ Fichier chargé: {len(self.audit_data.pages)} page(s) trouvée(s)")
        self.log(f"📂 Répertoire de sortie: {self._get_output_dir()}")

        # Check for duplicate URLs and warn
        url_to_pages = {}
        for page in self.audit_data.pages:
            if page.url and page.url not in ["Absente", ""]:
                if page.url in url_to_pages:
                    url_to_pages[page.url].append(page.page_id)
                else:
                    url_to_pages[page.url] = [page.page_id]

        for url, page_ids in url_to_pages.items():
            if len(page_ids) > 1:
                self.log(f"⚠️ ATTENTION: URL dupliquée - {url[:50]}... utilisée par: {', '.join(page_ids)}")

        # Log each page's URL for verification
        self.log("📋 URLs des pages:")
        for page in self.audit_data.pages:
            url_display = page.url[:60] + "..." if len(page.url) > 60 else page.url
            self.log(f"   {page.page_id}: {url_display}")

    def _open_log_file(self):
        """Open the log file for auto-saving."""
        try:
            # Close previous log file if open
            if self._log_file:
                self._log_file.close()

            # Create log file path in output directory
            import os
            output_dir = self._get_output_dir()
            self._log_file_path = os.path.join(output_dir, "audit_journal.log")

            # Open in append mode
            self._log_file = open(self._log_file_path, 'a', encoding='utf-8')

            # Write session separator
            from datetime import datetime
            self._log_file.write(f"\n{'=' * 60}\n")
            self._log_file.write(f"Session: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self._log_file.write(f"Fichier: {self.file_path_var.get()}\n")
            self._log_file.write(f"Répertoire de sortie: {output_dir}\n")
            self._log_file.write(f"{'=' * 60}\n")
            self._log_file.flush()
        except Exception:
            self._log_file = None

    def _make_page_logger(self, page_id: str):
        """
        Create a logger that writes to both the general log and a page-specific log file.

        Args:
            page_id: Page identifier (P01, P02, etc.)

        Returns:
            Tuple of (page_logger_function, page_log_file_handle)
        """
        import os
        from datetime import datetime

        output_dir = self._get_output_dir()
        log_path = os.path.join(output_dir, f"{page_id}.log")

        try:
            page_file = open(log_path, 'w', encoding='utf-8')
            page_file.write(f"{'=' * 60}\n")
            page_file.write(f"Log {page_id} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            page_file.write(f"{'=' * 60}\n")
            page_file.flush()
        except Exception:
            page_file = None

        def page_logger(message):
            # Write to general log (thread-safe via self.after)
            self.log(message)
            # Write to page-specific log file
            if page_file:
                try:
                    page_file.write(f"{message}\n")
                    page_file.flush()
                except Exception:
                    pass

        return page_logger, page_file

    def _close_page_logger(self, page_log_file):
        """Close a page-specific log file handle."""
        if page_log_file:
            try:
                page_log_file.close()
            except Exception:
                pass

    def _load_file_error(self, error_msg: str):
        """Called when file loading fails."""
        messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{error_msg}")
        self.log(f"❌ Erreur: {error_msg}")

    def populate_pages_list(self):
        """Populate the pages treeview."""
        # Clear existing items
        for item in self.pages_tree.get_children():
            self.pages_tree.delete(item)

        # Add pages
        for page in self.audit_data.pages:
            stats = page.get_statistics()
            status_text = self._format_page_status(stats)

            # Determine if page has been actually tested (has C or NC results, not just NA)
            # A page is "checked" only if it has at least one C or NC result
            is_checked = (stats['compliant'] + stats['non_compliant']) > 0
            row_tag = "checked" if is_checked else "not_checked"

            self.pages_tree.insert(
                "",
                "end",
                values=(
                    page.page_id,
                    page.title or "(Sans titre)",
                    page.url or "(Absente)",
                    status_text
                ),
                tags=(row_tag,)
            )

    def _format_page_status(self, stats: dict) -> str:
        """Format page status for display."""
        if stats['not_tested'] == stats['total']:
            return "Non testé"
        elif stats['compliant'] == stats['total']:
            return "✅ Conforme"
        elif stats['not_applicable'] == stats['total']:
            return "N/A"
        else:
            return f"{stats['compliant']}/{stats['total']} ✓"

    def analyze_selected_page(self):
        """Analyze the currently selected page."""
        selection = self.pages_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une page")
            return

        # Get selected page ID
        values = self.pages_tree.item(selection[0], "values")
        page_id = values[0]

        # Run analysis in thread
        thread = threading.Thread(
            target=self._analyze_page_thread,
            args=(page_id,),
            daemon=True
        )
        thread.start()

    def _analyze_page_thread(self, page_id: str):
        """Analyze a page in a separate thread."""
        # Update output directory for CSV files
        self._update_analyzer_output_dir()

        # Create per-page logger
        page_logger, page_log_file = self._make_page_logger(page_id)

        try:
            # Get page info
            page_info = self.audit_handler.get_page_audit(page_id)
            title = page_info.title if page_info else ""
            url = page_info.url if page_info else ""

            page_logger("=" * 50)
            page_logger(f"📄 Analyse de {page_id}: {title}")
            if url:
                page_logger(f"🔗 {url}")
            page_logger("=" * 50)

            # Set up crawler logging callback to page logger
            if self.audit_analyzer and self.audit_analyzer.crawler:
                self.audit_analyzer.crawler.definir_callback_log(page_logger)

            page = self.audit_analyzer.analyze_page(page_id, run_automated_tests=True)

            if page:
                stats = page.get_statistics()
                page_logger("")
                page_logger("✅ ANALYSE TERMINÉE!")
                page_logger(f"📊 Résultats pour {page_id}:")
                page_logger(f"   - Conformes (C): {stats['compliant']}")
                page_logger(f"   - Non conformes (NC): {stats['non_compliant']}")
                page_logger(f"   - Non applicables (NA): {stats['not_applicable']}")
                page_logger(f"   - Non testés (NT): {stats['not_tested']}")

                # Auto-save results
                try:
                    self.audit_handler.save()
                    page_logger("💾 Résultats sauvegardés automatiquement")
                except Exception as save_error:
                    page_logger(f"⚠️ Avertissement: Sauvegarde échouée - {str(save_error)}")

                # Update UI and show completion message
                self.after(0, self.populate_pages_list)
                self.after(0, lambda: self._show_page_analysis_complete(page_id, stats))
            else:
                page_logger(f"❌ Impossible d'analyser la page {page_id}")
                self.after(0, lambda: messagebox.showerror("Erreur", f"Impossible d'analyser la page {page_id}"))

        except Exception as e:
            page_logger(f"❌ Erreur lors de l'analyse: {str(e)}")
            import traceback
            page_logger(f"Détails: {traceback.format_exc()}")
            self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}"))
        finally:
            self._close_page_logger(page_log_file)

    def _show_page_analysis_complete(self, page_id: str, stats: dict):
        """Show page analysis completion message."""
        message = (
            f"Analyse de {page_id} terminée!\n\n"
            f"📊 Résultats:\n"
            f"  • Conformes (C): {stats['compliant']}\n"
            f"  • Non conformes (NC): {stats['non_compliant']}\n"
            f"  • Non applicables (NA): {stats['not_applicable']}\n"
            f"  • Non testés (NT): {stats['not_tested']}\n\n"
            f"Les résultats ont été sauvegardés."
        )
        messagebox.showinfo("Analyse terminée", message)

    def analyze_all_pages(self):
        """Analyze all pages in the audit file."""
        if not self.audit_handler:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier")
            return

        # Confirm action
        if not messagebox.askyesno("Confirmation", "Analyser toutes les pages? Cela peut prendre plusieurs minutes."):
            return

        # Run analysis in thread
        thread = threading.Thread(
            target=self._analyze_all_pages_thread,
            daemon=True
        )
        thread.start()

    def _analyze_all_pages_thread(self):
        """Analyze all pages in a separate thread."""
        try:
            parallel_enabled = self.parallel_enabled.get()
            num_workers = self.parallel_workers.get()

            # Update output directory for CSV files
            self._update_analyzer_output_dir()
            output_dir = self._get_output_dir()

            self.log("=" * 50)
            if parallel_enabled:
                self.log(f"Début de l'analyse parallèle ({num_workers} threads)...")
            else:
                self.log("Début de l'analyse séquentielle...")
            self.log(f"📂 Répertoire de sortie: {output_dir}")
            self.log("=" * 50)

            # Set up crawler logging callback
            if self.audit_analyzer and self.audit_analyzer.crawler:
                self.audit_analyzer.crawler.definir_callback_log(self.log)

            # Get pages info for display
            pages = self.audit_handler.get_sample_pages()
            total = len(pages)

            if parallel_enabled:
                # Parallel analysis
                stats = self._analyze_pages_parallel(pages, num_workers)
            else:
                # Sequential analysis with per-page log files
                for i, page_info in enumerate(pages):
                    page_id = page_info['page_id']
                    title = page_info['title']
                    url = page_info['url']

                    # Create per-page logger
                    page_logger, page_log_file = self._make_page_logger(page_id)

                    try:
                        page_logger("")
                        page_logger(f"📄 [{i + 1}/{total}] Analyse de {page_id}: {title}")
                        if url:
                            page_logger(f"   🔗 {url}")

                        # Set crawler callback to page logger
                        if self.audit_analyzer and self.audit_analyzer.crawler:
                            self.audit_analyzer.crawler.definir_callback_log(page_logger)

                        self.audit_analyzer.analyze_page(page_id, run_automated_tests=True)
                    except Exception as e:
                        page_logger(f"⚠️ Erreur lors de l'analyse de {page_id}: {str(e)}")
                    finally:
                        self._close_page_logger(page_log_file)

                stats = self.audit_handler.calculate_synthesis()

            self.log("")
            self.log("=" * 50)
            self.log("✅ ANALYSE TERMINÉE!")
            self.log("=" * 50)
            self.log(f"📊 Résultats:")
            self.log(f"   - Conformes (C): {stats['compliant']}")
            self.log(f"   - Non conformes (NC): {stats['non_compliant']}")
            self.log(f"   - Non applicables (NA): {stats['not_applicable']}")
            self.log(f"   - Non testés (NT): {stats['not_tested']}")

            # Auto-save results
            try:
                self.audit_handler.save()
                self.log("💾 Résultats sauvegardés automatiquement")
            except Exception as save_error:
                self.log(f"⚠️ Avertissement: Sauvegarde échouée - {str(save_error)}")

            # Update UI and show completion message
            self.after(0, self.populate_pages_list)
            self.after(0, lambda: self._show_analysis_complete(stats))

        except Exception as e:
            self.log(f"❌ Erreur lors de l'analyse: {str(e)}")
            import traceback
            self.log(f"Détails: {traceback.format_exc()}")
            self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{str(e)}"))

    def _analyze_pages_parallel(self, pages: list, num_workers: int) -> dict:
        """
        Analyze pages in parallel using ThreadPoolExecutor.

        Args:
            pages: List of page info dictionaries
            num_workers: Number of parallel workers

        Returns:
            Statistics dictionary
        """
        import threading

        total = len(pages)
        completed = [0]  # Use list to allow modification in nested function
        lock = threading.Lock()

        def analyze_single_page(page_info):
            """Analyze a single page (runs in worker thread)."""
            page_id = page_info['page_id']
            title = page_info['title']
            url = page_info['url']

            # Create per-page logger for this thread
            page_logger, page_log_file = self._make_page_logger(page_id)

            # Log start (thread-safe via self.log using after())
            with lock:
                completed[0] += 1
                current = completed[0]

            page_logger("")
            page_logger(f"📄 [{current}/{total}] Analyse de {page_id}: {title}")
            if url:
                page_logger(f"   🔗 {url}")

            try:
                # Each thread needs its own crawler for HTTP requests
                from .crawler import Crawler
                from .ods_analyzer import ODSAuditAnalyzer

                # Create a thread-local analyzer that shares the handler
                thread_analyzer = ODSAuditAnalyzer.__new__(ODSAuditAnalyzer)
                thread_analyzer.handler = self.audit_handler
                thread_analyzer.config = self.config
                thread_analyzer.crawler = Crawler(self.config)
                thread_analyzer.crawler.definir_callback_log(page_logger)
                thread_analyzer.full_rgaa_mode = True
                thread_analyzer.analyseur = None
                thread_analyzer.output_dir = self._get_output_dir()

                # Analyze the page
                thread_analyzer.analyze_page(page_id, run_automated_tests=True)

                return {'page_id': page_id, 'success': True}

            except Exception as e:
                page_logger(f"⚠️ Erreur {page_id}: {str(e)}")
                return {'page_id': page_id, 'success': False, 'error': str(e)}
            finally:
                self._close_page_logger(page_log_file)

        # Run analysis in parallel
        self.log(f"🚀 Lancement de {num_workers} workers parallèles...")

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(analyze_single_page, page): page for page in pages}

            for future in as_completed(futures):
                result = future.result()
                # Results are logged within each worker

        # Calculate final statistics
        return self.audit_handler.calculate_synthesis()

    def _show_analysis_complete(self, stats: dict):
        """Show analysis completion message."""
        message = (
            f"Analyse de toutes les pages terminée!\n\n"
            f"📊 Résultats:\n"
            f"  • Conformes (C): {stats['compliant']}\n"
            f"  • Non conformes (NC): {stats['non_compliant']}\n"
            f"  • Non applicables (NA): {stats['not_applicable']}\n"
            f"  • Non testés (NT): {stats['not_tested']}\n\n"
            f"Les résultats ont été sauvegardés automatiquement."
        )
        messagebox.showinfo("Analyse terminée", message)

    def save_results(self):
        """Save the audit results to ODS file."""
        if not self.audit_handler:
            messagebox.showwarning("Attention", "Aucun fichier chargé")
            return

        # Ask for output file
        output_path = filedialog.asksaveasfilename(
            title="Enregistrer les résultats",
            defaultextension=".ods",
            filetypes=[("OpenDocument Spreadsheet", "*.ods")],
            initialfile="audit_resultats.ods"
        )

        if not output_path:
            return

        try:
            self.log(f"Enregistrement des résultats dans {output_path}...")
            self.audit_handler.save(output_path)
            self.log(f"✅ Résultats enregistrés: {output_path}")
            messagebox.showinfo("Succès", f"Résultats enregistrés:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer:\n{str(e)}")
            self.log(f"❌ Erreur: {str(e)}")

    def show_statistics(self):
        """Show statistics in a popup window."""
        if not self.audit_handler:
            messagebox.showwarning("Attention", "Aucun fichier chargé")
            return

        try:
            summary = self.audit_analyzer.generate_report_summary()

            # Create popup window
            stats_window = tk.Toplevel(self)
            stats_window.title("Statistiques de l'audit")
            stats_window.geometry("600x500")

            # Add text widget with scrollbar
            text_frame = ttk.Frame(stats_window, padding=10)
            text_frame.pack(fill="both", expand=True)

            text_widget = scrolledtext.ScrolledText(text_frame, wrap="word")
            text_widget.pack(fill="both", expand=True)
            text_widget.insert("1.0", summary)
            text_widget.config(state="disabled")

            # Close button
            ttk.Button(stats_window, text="Fermer", command=stats_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer les statistiques:\n{str(e)}")

    def view_log(self):
        """View and export the log content."""
        # Get current log content
        log_content = self.log_text.get("1.0", "end-1c")

        if not log_content.strip():
            messagebox.showinfo("Journal", "Le journal est vide")
            return

        # Create popup window
        log_window = tk.Toplevel(self)
        log_window.title("Journal d'activité")
        log_window.geometry("800x600")

        # Add text widget with scrollbar
        text_frame = ttk.Frame(log_window, padding=10)
        text_frame.pack(fill="both", expand=True)

        text_widget = scrolledtext.ScrolledText(text_frame, wrap="word")
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", log_content)
        text_widget.config(state="disabled")

        # Buttons frame
        button_frame = ttk.Frame(log_window, padding=10)
        button_frame.pack(fill="x")

        def save_log():
            """Save log to file."""
            output_path = filedialog.asksaveasfilename(
                title="Enregistrer le journal",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="audit_journal.txt"
            )
            if output_path:
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(log_content)
                    messagebox.showinfo("Succès", f"Journal enregistré:\n{output_path}")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'enregistrer le journal:\n{str(e)}")

        ttk.Button(button_frame, text="💾 Enregistrer", command=save_log).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Fermer", command=log_window.destroy).pack(side="left", padx=5)

    def clear_status(self):
        """Clear all status values and reset to NOT_TESTED."""
        if not self.audit_handler:
            messagebox.showwarning("Attention", "Aucun fichier chargé")
            return

        # Confirm action
        result = messagebox.askyesno(
            "Confirmation",
            "Réinitialiser tous les statuts à 'Non testé' ?\n\n"
            "Cette action réinitialisera toutes les évaluations de toutes les pages.\n"
            "Les commentaires et modifications seront effacés.\n\n"
            "Note : Les critères marqués 'NA' (Non Applicable) seront préservés."
        )

        if not result:
            return

        try:
            self.log("Réinitialisation des statuts...")

            # Reset all pages, but preserve NA statuses
            reset_count = 0
            skipped_na_count = 0
            for page in self.audit_data.pages:
                for criterion in page.criteria:
                    # Skip criteria that are already marked as NA
                    if criterion.status == Status.NOT_APPLICABLE:
                        skipped_na_count += 1
                        continue

                    self.audit_handler.update_criterion(
                        page_id=page.page_id,
                        criterion_id=criterion.criterion_id,
                        status=Status.NOT_TESTED,
                        derogation=Derogation.NO,
                        modifications="",
                        comments=""
                    )
                    reset_count += 1

            # Save changes
            self.audit_handler.save()

            self.log(f"✅ {reset_count} critère(s) réinitialisé(s)")
            if skipped_na_count > 0:
                self.log(f"⊘ {skipped_na_count} critère(s) NA préservé(s)")
            self.log("💾 Modifications sauvegardées")

            # Update UI
            self.populate_pages_list()

            message = f"{reset_count} critère(s) réinitialisé(s) à 'Non testé'"
            if skipped_na_count > 0:
                message += f"\n{skipped_na_count} critère(s) NA préservé(s)"
            messagebox.showinfo("Succès", message)

        except Exception as e:
            self.log(f"❌ Erreur lors de la réinitialisation: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de réinitialiser:\n{str(e)}")

    def log(self, message: str):
        """
        Add a message to the log output.
        Thread-safe: can be called from any thread.

        Args:
            message: Message to log
        """
        # Schedule GUI update on main thread
        self.after(0, self._log_internal, message)

    def _log_internal(self, message: str):
        """Internal log method that runs on main thread."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

        # Auto-save to log file
        if self._log_file:
            try:
                self._log_file.write(f"{message}\n")
                self._log_file.flush()
            except Exception:
                pass
