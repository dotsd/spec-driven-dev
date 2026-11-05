"""Unified Traceability Correlator linking Requirements & Tickets to Code."""

from __future__ import annotations

import re
from typing import Sequence
from .models import FileNode, RequirementNode, TicketNode, TraceabilityLink


class TraceabilityCorrelator:
    """Discovers and establishes cross-reference links between functional artifacts and technical code."""

    def correlate(
        self,
        files: dict[str, FileNode],
        requirements: Sequence[RequirementNode],
        tickets: Sequence[TicketNode],
    ) -> list[TraceabilityLink]:
        links: list[TraceabilityLink] = []
        seen_links: set[tuple[str, str, str]] = set()

        def _add_link(
            item_id: str,
            item_type: str,
            source_doc: str,
            title: str,
            code_file: str,
            symbol_or_route: str | None,
            match_reason: str,
        ) -> None:
            key = (item_id, code_file, symbol_or_route or "")
            if key not in seen_links:
                seen_links.add(key)
                links.append(
                    TraceabilityLink(
                        item_id=item_id,
                        item_type=item_type,
                        source_doc=source_doc,
                        title=title,
                        code_file=code_file,
                        symbol_or_route=symbol_or_route,
                        match_reason=match_reason,
                    )
                )

        # Build index of code routes and models
        route_index: dict[str, tuple[str, str]] = {}  # route_path -> (file_path, method)
        model_index: dict[str, tuple[str, str]] = {}  # model_name.lower() -> (file_path, model_name)

        for fpath, fnode in files.items():
            for r in fnode.routes:
                route_index[r.path.lower()] = (fpath, f"{r.method} {r.path}")
            for m in fnode.models:
                model_index[m.name.lower()] = (fpath, m.name)

        # 1. Correlate Requirements
        for req in requirements:
            req_id_lower = req.id.lower()
            req_text = f"{req.title} {req.description or ''} {' '.join(req.acceptance_criteria)}".lower()

            # Spec directory correlation: e.g. specs/001-user-auth/ -> src/auth or files with user/auth
            spec_feature_match = re.search(r"""specs/([0-9A-Za-z_-]+)/""", req.source_doc)
            feature_name = spec_feature_match.group(1).lower() if spec_feature_match else ""
            cleaned_feature = re.sub(r"""^\d+[-_]""", "", feature_name)

            for fpath, fnode in files.items():
                fpath_lower = fpath.lower()

                # Feature directory match
                if cleaned_feature and len(cleaned_feature) > 2 and cleaned_feature in fpath_lower:
                    _add_link(
                        item_id=req.id,
                        item_type="requirement",
                        source_doc=req.source_doc,
                        title=req.title,
                        code_file=fpath,
                        symbol_or_route=None,
                        match_reason="spec_feature_module",
                    )

                # Check explicit references in routes/symbols
                for sym_id in fnode.symbols:
                    if req_id_lower in sym_id.lower():
                        _add_link(
                            item_id=req.id,
                            item_type="requirement",
                            source_doc=req.source_doc,
                            title=req.title,
                            code_file=fpath,
                            symbol_or_route=sym_id,
                            match_reason="explicit_tag",
                        )

            # Route co-occurrence in requirement text
            for rpath, (code_file, route_label) in route_index.items():
                if len(rpath) > 3 and rpath in req_text:
                    _add_link(
                        item_id=req.id,
                        item_type="requirement",
                        source_doc=req.source_doc,
                        title=req.title,
                        code_file=code_file,
                        symbol_or_route=route_label,
                        match_reason="route_path",
                    )

            # Model co-occurrence in requirement text
            for mname, (code_file, original_name) in model_index.items():
                if len(mname) > 3 and re.search(rf"\b{re.escape(mname)}\b", req_text):
                    _add_link(
                        item_id=req.id,
                        item_type="requirement",
                        source_doc=req.source_doc,
                        title=req.title,
                        code_file=code_file,
                        symbol_or_route=f"Model: {original_name}",
                        match_reason="domain_model",
                    )

        # 2. Correlate Tickets
        for ticket in tickets:
            t_key_lower = ticket.key.lower()
            t_text = f"{ticket.summary} {ticket.description or ''} {' '.join(ticket.components)}".lower()

            for fpath, fnode in files.items():
                fpath_lower = fpath.lower()

                # Match by explicit ticket key in file path or symbol
                if t_key_lower in fpath_lower:
                    _add_link(
                        item_id=ticket.key,
                        item_type="ticket",
                        source_doc=ticket.source_file,
                        title=ticket.summary,
                        code_file=fpath,
                        symbol_or_route=None,
                        match_reason="ticket_key_in_path",
                    )

                # Match by target subsystem or component
                for comp in ticket.components:
                    comp_lower = comp.lower()
                    if len(comp_lower) > 2 and comp_lower in fpath_lower:
                        _add_link(
                            item_id=ticket.key,
                            item_type="ticket",
                            source_doc=ticket.source_file,
                            title=ticket.summary,
                            code_file=fpath,
                            symbol_or_route=None,
                            match_reason=f"subsystem_{comp_lower}",
                        )

            # Route co-occurrence in ticket text
            for rpath, (code_file, route_label) in route_index.items():
                if len(rpath) > 3 and rpath in t_text:
                    _add_link(
                        item_id=ticket.key,
                        item_type="ticket",
                        source_doc=ticket.source_file,
                        title=ticket.summary,
                        code_file=code_file,
                        symbol_or_route=route_label,
                        match_reason="route_path",
                    )

            # Model co-occurrence in ticket text
            for mname, (code_file, original_name) in model_index.items():
                if len(mname) > 3 and re.search(rf"\b{re.escape(mname)}\b", t_text):
                    _add_link(
                        item_id=ticket.key,
                        item_type="ticket",
                        source_doc=ticket.source_file,
                        title=ticket.summary,
                        code_file=code_file,
                        symbol_or_route=f"Model: {original_name}",
                        match_reason="domain_model",
                    )

        return links
