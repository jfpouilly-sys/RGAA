# -*- coding: utf-8 -*-
"""
GUI components for ODS-based RGAA audit analysis.

Provides Tkinter interface for working with grilleAudit.ods files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
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

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # File selection section
        self._create_file_section()

        # Audit information section
        self._create_info_section()

        # Pages list section
        self._create_pages_section()

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

        self.pages_tree.pack(fill="both", expand=True)

        # Add context menu
        self.pages_tree.bind("<Double-1>", lambda e: self.analyze_selected_page())

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

    def load_file(self):
        """Load the ODS file and display audit information."""
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier ODS")
            return

        try:
            self.log("Chargement du fichier d'audit...")

            self.audit_handler = RGAAAuditODSHandler(filepath)
            self.audit_data = self.audit_handler.load()
            self.audit_analyzer = ODSAuditAnalyzer(self.audit_handler, self.config)

            # Update info labels
            self.info_labels['date'].config(text=self.audit_data.date or "-")
            self.info_labels['auditor'].config(text=self.audit_data.auditor or "-")
            self.info_labels['context'].config(text=self.audit_data.context or "-")
            self.info_labels['site'].config(text=self.audit_data.site_url or "-")

            # Populate pages list
            self.populate_pages_list()

            self.log(f"✅ Fichier chargé: {len(self.audit_data.pages)} page(s) trouvée(s)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{str(e)}")
            self.log(f"❌ Erreur: {str(e)}")

    def populate_pages_list(self):
        """Populate the pages treeview."""
        # Clear existing items
        for item in self.pages_tree.get_children():
            self.pages_tree.delete(item)

        # Add pages
        for page in self.audit_data.pages:
            stats = page.get_statistics()
            status_text = self._format_page_status(stats)

            self.pages_tree.insert(
                "",
                "end",
                values=(
                    page.page_id,
                    page.title or "(Sans titre)",
                    page.url or "(Absente)",
                    status_text
                )
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
        try:
            self.log(f"Analyse de la page {page_id}...")

            page = self.audit_analyzer.analyze_page(page_id, run_automated_tests=True)

            if page:
                stats = page.get_statistics()
                self.log(f"✅ Page {page_id} analysée: {stats['compliant']}/{stats['total'] - stats['not_applicable']} conformes")

                # Update UI
                self.after(0, self.populate_pages_list)
            else:
                self.log(f"❌ Impossible d'analyser la page {page_id}")

        except Exception as e:
            self.log(f"❌ Erreur lors de l'analyse: {str(e)}")

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
            self.log("Début de l'analyse de toutes les pages...")

            def progress_callback(page_id, current, total):
                self.log(f"Analyse {current}/{total}: {page_id}...")

            stats = self.audit_analyzer.analyze_all_pages(progress_callback=progress_callback)

            self.log("✅ Analyse terminée!")
            self.log(f"Résultats: {stats['compliant']} conformes, {stats['non_compliant']} non conformes, {stats['not_applicable']} N/A")

            # Update UI
            self.after(0, self.populate_pages_list)

        except Exception as e:
            self.log(f"❌ Erreur lors de l'analyse: {str(e)}")

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

    def log(self, message: str):
        """
        Add a message to the log output.

        Args:
            message: Message to log
        """
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
