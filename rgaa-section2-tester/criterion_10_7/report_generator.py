"""
Generation du rapport Markdown pour le critere 10.7.
Suit le format ISIT de rapport d'audit RGAA.

Le rapport inclut :
    - Synthese globale avec tableau de statuts par page
    - Analyse des feuilles de style (regles de suppression detectees)
    - Detail par page avec elements NC, A verifier, et C
    - Guide de verification manuelle pour les cas ambigus
"""

from datetime import datetime
from .focus_tester import PageFocusResult
from .constants import FocusStatus


class FocusReportGenerator:
    """Genere le rapport d'analyse du critere 10.7."""

    def generate(self, results: list[PageFocusResult],
                 output_path: str,
                 site_name: str = "Site audite"):
        """
        Genere un rapport Markdown complet.

        Args:
            results: Liste des resultats par page
            output_path: Chemin du fichier de sortie
            site_name: Nom du site audite

        Returns:
            Chemin du fichier genere
        """
        lines = []

        # En-tete
        lines.append("# Rapport d'analyse automatisee — Critere RGAA 10.7")
        lines.append("# Visibilite du focus")
        lines.append("")
        lines.append(f"**Site** : {site_name}")
        lines.append(
            f"**Date d'analyse** : "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        lines.append("**Outil** : RGAA Focus Tester (analyse automatisee)")
        lines.append(f"**Pages analysees** : {len(results)}")
        lines.append("")

        # Avertissement
        lines.append("---")
        lines.append("")
        lines.append(
            "## Avertissement — Limites de l'analyse automatisee"
        )
        lines.append("")
        lines.append(
            "Ce rapport est genere par un outil d'analyse automatisee. "
            "**Il ne constitue pas un audit complet** du critere RGAA 10.7. "
            "Les limitations suivantes s'appliquent :"
        )
        lines.append("")
        lines.append(
            "- **Detection fiable** : suppression de l'outline CSS "
            "(`outline: none`, `outline: 0`) sans style compensatoire. "
            "Ces cas sont identifies comme Non Conformes avec haute confiance."
        )
        lines.append(
            "- **Detection partielle** : styles de focus personnalises "
            "(box-shadow, border, background). L'outil detecte leur presence "
            "mais ne peut pas evaluer si le contraste et la taille de "
            "l'indicateur sont suffisants pour etre percus par tous les "
            "utilisateurs."
        )
        lines.append(
            "- **Non detecte** : indicateurs de focus geres dynamiquement "
            "par JavaScript, transitions CSS complexes, focus visible "
            "uniquement via `:focus-visible` (gere par le navigateur selon "
            "l'heuristique de saisie), ou styles dependant de media queries."
        )
        lines.append("")
        lines.append(
            "**L'auditeur doit imperativement verifier visuellement "
            "tous les elements marques 'A verifier' en naviguant au clavier "
            "(touche Tab) sur chaque page.**"
        )
        lines.append("")

        # Synthese globale
        lines.append("---")
        lines.append("")
        lines.append("## Synthese globale")
        lines.append("")

        total_c = sum(r.total_conforme for r in results)
        total_nc = sum(r.total_non_conforme for r in results)
        total_av = sum(r.total_a_verifier for r in results)
        total_el = sum(r.total_visible for r in results)

        lines.append("| Indicateur | Valeur |")
        lines.append("|-----------|--------|")
        lines.append(f"| Pages analysees | {len(results)} |")
        lines.append(
            f"| Elements focusables visibles (total) | {total_el} |"
        )
        lines.append(
            f"| Elements conformes (focus visible) | {total_c} |"
        )
        lines.append(
            f"| Elements non conformes (focus supprime) | {total_nc} |"
        )
        lines.append(
            f"| Elements a verifier manuellement | {total_av} |"
        )
        lines.append("")

        # Tableau de synthese par page
        lines.append("### Statut suggere par page")
        lines.append("")
        lines.append(
            "| Page | URL | Elements | C | NC | A verifier "
            "| Statut suggere | Confiance |"
        )
        lines.append(
            "|------|-----|----------|---|----|-----------"
            "|--------------:|-----------|"
        )

        for r in results:
            url_short = (
                r.url[:60] + "..." if len(r.url) > 60 else r.url
            )
            status_display = {
                FocusStatus.CONFORME: "C",
                FocusStatus.NON_CONFORME: "NC",
                FocusStatus.A_VERIFIER: "NT",
                FocusStatus.NON_APPLICABLE: "NA",
            }.get(r.suggested_status, "?")

            lines.append(
                f"| {r.page_id} | {url_short} | {r.total_visible} | "
                f"{r.total_conforme} | {r.total_non_conforme} | "
                f"{r.total_a_verifier} | {status_display} | "
                f"{r.confidence} |"
            )

        lines.append("")

        # Analyse des feuilles de style (si pertinente)
        any_global = any(
            r.stylesheet_analysis.get('global_outline_none')
            for r in results
        )
        any_suppression = any(
            r.stylesheet_analysis.get('suppression_rules')
            for r in results
        )

        if any_global or any_suppression:
            lines.append("---")
            lines.append("")
            lines.append("## Analyse des feuilles de style")
            lines.append("")

            if any_global:
                lines.append(
                    "**ALERTE** : Une regle CSS globale de suppression de "
                    "l'outline a ete detectee "
                    "(`* { outline: none }` ou similaire). "
                    "Cette pratique supprime l'indicateur de focus natif du "
                    "navigateur pour TOUS les elements et constitue une "
                    "non-conformite sauf si un style de focus personnalise "
                    "est defini pour chaque element focusable."
                )
                lines.append("")

            for r in results:
                supp_rules = r.stylesheet_analysis.get(
                    'suppression_rules', []
                )
                if supp_rules:
                    lines.append(
                        f"### {r.page_id} — Regles de suppression detectees"
                    )
                    lines.append("")
                    for rule in supp_rules[:10]:
                        lines.append("```css")
                        lines.append(f"{rule.get('cssText', '')}")
                        lines.append("```")
                        lines.append("")

        # Detail par page
        lines.append("---")
        lines.append("")
        lines.append("## Detail par page")
        lines.append("")

        for r in results:
            lines.append(f"### {r.page_id} — {r.url}")
            lines.append("")
            lines.append(
                f"**Statut suggere** : {r.suggested_status} "
                f"(confiance : {r.confidence})"
            )
            lines.append(f"**Detail** : {r.details}")
            lines.append("")

            # Elements non conformes (en premier)
            nc_elements = [
                e for e in r.elements
                if e.status == FocusStatus.NON_CONFORME
            ]
            if nc_elements:
                lines.append(
                    f"#### Elements non conformes ({len(nc_elements)})"
                )
                lines.append("")
                for el in nc_elements:
                    lines.append(f"- **`{el.identifier}`**")
                    lines.append(f"  - {el.details}")
                    if el.visual_changes:
                        for vc in el.visual_changes[:3]:
                            lines.append(
                                f"  - `{vc['property']}`: "
                                f"`{vc['before']}` -> `{vc['after']}`"
                            )
                lines.append("")

            # Elements a verifier
            av_elements = [
                e for e in r.elements
                if e.status == FocusStatus.A_VERIFIER
            ]
            if av_elements:
                lines.append(
                    f"#### Elements a verifier ({len(av_elements)})"
                )
                lines.append("")
                for el in av_elements:
                    lines.append(f"- **`{el.identifier}`**")
                    lines.append(f"  - {el.details}")
                lines.append("")

            # Elements conformes (resume compact)
            c_elements = [
                e for e in r.elements
                if e.status == FocusStatus.CONFORME
            ]
            if c_elements:
                lines.append(
                    f"#### Elements conformes ({len(c_elements)})"
                )
                lines.append("")
                by_type = {}
                for el in c_elements:
                    key = el.tag_name
                    if key not in by_type:
                        by_type[key] = []
                    by_type[key].append(el)
                for tag, els in by_type.items():
                    if len(els) <= 3:
                        for el in els:
                            lines.append(
                                f"- `{el.identifier}` — {el.details}"
                            )
                    else:
                        lines.append(
                            f"- **{len(els)} `<{tag}>`** — focus natif "
                            f"preserve (ex: `{els[0].identifier}`)"
                        )
                lines.append("")

            lines.append("---")
            lines.append("")

        # Guide de verification manuelle
        lines.append(
            "## Guide de verification manuelle pour les elements "
            "'A verifier'"
        )
        lines.append("")
        lines.append(
            "Pour chaque element marque 'A verifier', l'auditeur doit :"
        )
        lines.append("")
        lines.append(
            "1. **Naviguer au clavier** (touche Tab) jusqu'a l'element "
            "concerne"
        )
        lines.append(
            "2. **Observer** si un indicateur visuel de focus est clairement "
            "visible (contour, ombre, changement de fond, soulignement...)"
        )
        lines.append(
            "3. **Evaluer le contraste** : l'indicateur doit etre "
            "suffisamment contraste par rapport a l'arriere-plan pour etre "
            "percu par un utilisateur ayant une vision normale"
        )
        lines.append(
            "4. **Tester avec differents fonds** si l'element apparait sur "
            "des fonds de couleur variable"
        )
        lines.append(
            "5. **Statuer** : Conforme (C) si l'indicateur est clairement "
            "visible, Non Conforme (NC) s'il est absent ou insuffisant"
        )
        lines.append("")
        lines.append(
            "**Reference** : RGAA 4.1.2 — Critere 10.7, Test 10.7.1 — "
            "WCAG 2.1 SC 2.4.7 Focus Visible (AA)"
        )
        lines.append("")

        # Ecriture du fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return output_path
