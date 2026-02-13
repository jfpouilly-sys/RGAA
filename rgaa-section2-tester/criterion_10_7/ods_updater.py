"""
Module d'integration ODS — mise a jour du critere 10.7 dans la grille d'audit.

Ne met a jour automatiquement QUE les pages avec confiance "haute".
Les pages avec confiance "moyenne" ou "faible" recoivent un commentaire
d'aide mais restent NT.

Format du commentaire :
    [AUTO] ... — pour les mises a jour automatiques (confiance haute)
    [AUTO-PARTIEL] ... — pour les commentaires d'aide (confiance basse)
"""

import os
import sys

# Ajouter le repertoire parent au path pour importer les modules existants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rgaa_tester.ods_handler import OdsHandler
    HAS_ODS_HANDLER = True
except ImportError:
    HAS_ODS_HANDLER = False

try:
    from pyexcel_ods3 import get_data, save_data
    HAS_PYEXCEL = True
except ImportError:
    HAS_PYEXCEL = False


class ODSFocusUpdater:
    """Met a jour la grille ODS pour le critere 10.7."""

    CRITERION_ID = "10.7"

    def update_grid(self, ods_path: str, results: list,
                    output_path: str = None):
        """
        Met a jour les feuilles P01-P20 de la grille ODS pour le critere 10.7.

        IMPORTANT : Ne met a jour QUE les pages avec confiance "haute".
        Les pages avec confiance "moyenne" ou "faible" restent NT.

        Args:
            ods_path: Chemin de la grille ODS source
            results: Liste de PageFocusResult
            output_path: Chemin de sortie (si None, ecrase le fichier source)
        """
        if output_path is None:
            output_path = ods_path

        if HAS_PYEXCEL:
            self._update_with_pyexcel(ods_path, results, output_path)
        elif HAS_ODS_HANDLER:
            self._update_with_ods_handler(ods_path, results, output_path)
        else:
            raise ImportError(
                "Aucune bibliotheque ODS disponible. "
                "Installez pyexcel-ods3 ou verifiez que ods_handler est "
                "accessible."
            )

    def _update_with_pyexcel(self, ods_path: str, results: list,
                              output_path: str):
        """Met a jour via pyexcel-ods3."""
        data = get_data(ods_path)

        for result in results:
            sheet_name = result.page_id
            if sheet_name not in data:
                continue

            sheet = data[sheet_name]

            for row_idx, row in enumerate(sheet):
                if (len(row) >= 2
                        and str(row[1]).strip() == self.CRITERION_ID):
                    if result.confidence == "haute":
                        while len(row) < 7:
                            row.append("")

                        row[3] = result.suggested_status
                        row[5] = (
                            f"[AUTO] {result.details}. "
                            f"Elements analyses : {result.total_visible}, "
                            f"C={result.total_conforme}, "
                            f"NC={result.total_non_conforme}. "
                            f"Analyse automatisee — confiance haute."
                        )
                    else:
                        while len(row) < 7:
                            row.append("")

                        row[5] = (
                            f"[AUTO-PARTIEL] {result.details}. "
                            f"Confiance {result.confidence} — "
                            f"verification manuelle requise."
                        )
                    break

        save_data(output_path, data)

    def _update_with_ods_handler(self, ods_path: str, results: list,
                                  output_path: str):
        """Met a jour via le module ods_handler existant."""
        handler = OdsHandler()
        audit_data = handler.load(ods_path)

        for result in results:
            page_id = result.page_id

            if result.confidence == "haute":
                status = result.suggested_status
                comment = (
                    f"[AUTO] {result.details}. "
                    f"Elements analyses : {result.total_visible}, "
                    f"C={result.total_conforme}, "
                    f"NC={result.total_non_conforme}. "
                    f"Analyse automatisee — confiance haute."
                )
            else:
                status = None
                comment = (
                    f"[AUTO-PARTIEL] {result.details}. "
                    f"Confiance {result.confidence} — "
                    f"verification manuelle requise."
                )

            handler.update_criterion(
                audit_data, page_id, self.CRITERION_ID,
                status=status, modifications=comment
            )

        handler.save(audit_data, output_path)
