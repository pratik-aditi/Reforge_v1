# Feature Specification: HTML Documentation Standard

**Feature Branch**: `015-html-documentation-standard`
**Created**: 2026-03-04
**Status**: Draft
**Input**: TCOS-RUMO project experience producing 38+ professional HTML documents with Stephen Few design system
**Depends On**: Generate command (010), extraction types (014), common extraction schema (009)

## Summary

Codify the HTML documentation standard used in the TCOS-RUMO project into the Reforge framework so all future projects automatically produce professional, self-contained HTML reports with:
- Stephen Few design system (white ground, minimal rules, high data-ink ratio, Georgia serif typography)
- Inline SVG diagrams rendered from PlantUML with interactive lightbox
- Separate HTML files per extraction type with a master index page
- Cross-document navigation and print-friendly styles
- Automatic splitting of large extraction types into domain sub-files

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate HTML Documentation (Priority: P0)

An AI agent operator runs `/reforge.generate html` to produce a complete set of self-contained HTML reports from all available extractions, with an index page, per-type documents, inline diagrams, and cross-document navigation.

**Acceptance Scenarios**:

1. **Given** completed extractions, **When** the operator runs `/reforge.generate html`, **Then** the system produces `index.html` and per-type HTML files in `$GENERATED_DIR/` with the Stephen Few design system applied.
2. **Given** an extraction type with >200 items, **When** HTML is generated, **Then** the type is automatically split into domain sub-files with a sub-index page.
3. **Given** generated HTML files, **When** any file is opened in a browser, **Then** all CSS and JS is inline (no external dependencies), diagrams are interactive (click-to-expand lightbox), and cross-document navigation links work.

---

### User Story 2 - Scoped HTML Generation (Priority: P1)

An operator runs `/reforge.generate html --scope business-rules` to generate HTML documentation for a single extraction type.

**Acceptance Scenarios**:

1. **Given** a completed business-rules extraction, **When** the operator runs `/reforge.generate html --scope business-rules`, **Then** only `business-rules.html` (or split sub-files) and `index.html` are generated.

## Design Decisions

1. **Self-contained HTML** — All CSS and JS inline in each file (no external dependencies)
2. **Stephen Few aesthetic** — White ground, minimal rules, high data-ink ratio, Georgia serif typography
3. **Inline SVG diagrams** — PlantUML rendered to SVG and embedded directly (no external image files)
4. **Interactive lightbox** — Click-to-expand diagrams with zoom, fit, keyboard shortcuts
5. **Automatic splitting** — Large extraction types auto-split into domain sub-files with index
6. **Cross-document nav** — All files in a cluster link to siblings and master index
7. **Print-friendly** — `@media print` styles included, page breaks at section boundaries
8. **Source-anchored** — All generation constraints apply; `<!-- Source: ... -->` comments throughout
9. **HTML as default** — `html` is the recommended default format for `/reforge.generate`
