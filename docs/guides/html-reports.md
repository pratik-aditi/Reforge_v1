# HTML Reports

Reforge generates self-contained HTML documentation using a design system inspired by Stephen Few's data visualization principles. HTML is the recommended default format for `/reforge.generate`.

## Usage

=== "Claude Code"

    ```
    /reforge.generate html
    ```

=== "GitHub Copilot"

    ```
    @reforge.generate html
    ```

To generate documentation for a single extraction type:

=== "Claude Code"

    ```
    /reforge.generate html --scope business-rules
    ```

=== "GitHub Copilot"

    ```
    @reforge.generate html --scope business-rules
    ```

The `--scope` option accepts any extraction type name: `business-rules`, `database`, `ui`, `workflows`, `call-sites`, `dependencies`, `functional-requirements`, `non-functional`, `architecture`, `issues`.

## Design System

The HTML reports follow Stephen Few's principles for effective information display:

| Principle | Implementation |
|-----------|----------------|
| **White ground** | Clean white background with no decorative elements |
| **Minimal rules** | Thin, light-colored borders used only where they aid comprehension |
| **High data-ink ratio** | Maximum information density with minimum visual noise |
| **Georgia serif typography** | Body text in Georgia for readability; system sans-serif for labels and navigation |
| **Muted color palette** | Dark ink (`#1a1a1a`) for text, blue (`#2a6496`) for data and links, red (`#c0392b`) for alerts |

### Typography

- **Body text**: Georgia, 'Times New Roman', serif at 16px with 1.65 line height
- **Labels and navigation**: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif
- **Code**: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace at 0.88rem
- **Max content width**: 780px, centered

## Self-Contained HTML

Every generated HTML file is fully self-contained:

- All CSS is inlined within a `<style>` tag -- no external stylesheets
- All JavaScript is inlined within `<script>` tags -- no external scripts
- Diagrams are embedded as inline SVG -- no external image files
- No CDN dependencies, no network requests required

!!! info
    This means you can share individual HTML files via email, store them in document management systems, or open them offline. Each file works independently.

## Output Structure

A full HTML generation produces:

```
reforge_output/<project>/generated/
├── index.html              # Master index linking all documents
├── business-rules.html     # Business rules catalog
├── database.html           # Database interactions and data model
├── ui-flows.html           # UI components and navigation flows
├── workflows.html          # Workflow and process documentation
├── call-sites.html         # Call relationship catalog
├── dependencies.html       # Module dependency documentation
├── functional-requirements.html
├── non-functional.html     # NFRs and security findings
├── architecture.html       # Architectural components and patterns
└── issues.html             # Issues and technical debt catalog
```

The **master index page** (`index.html`) contains:

- Summary statistics (extraction types, total items, coverage percentage)
- Links to all per-type documents, organized into Core and Extended sections
- Item counts and generation dates for each document

## Inline SVG Diagrams

Diagrams are rendered from PlantUML notation into SVG and embedded directly in the HTML:

- PlantUML source is converted to SVG at generation time
- SVG markup is inlined in the HTML document (no external `.svg` files)
- Each diagram is wrapped in a `<figure>` element with a caption

### Interactive Lightbox

Clicking any diagram opens an interactive lightbox overlay with:

- **Zoom controls** -- zoom in and out for detailed inspection
- **Fit-to-screen** -- reset to fit the entire diagram in the viewport
- **Keyboard shortcuts** -- `Escape` to close, `+`/`-` to zoom
- **Click-outside-to-close** -- click the overlay background to dismiss

The lightbox JavaScript is inlined in every HTML file, so it works offline and in any browser.

## Cross-Document Navigation

Every per-type HTML file includes:

- A **header navigation bar** with links to all sibling documents and the master index
- **Breadcrumb-style context** showing the current document within the documentation set
- **Footer navigation** with links to the previous and next documents in the set

Navigation links are relative paths, so the entire documentation set can be moved as a folder without breaking links.

## Automatic Splitting

When an extraction type produces more than **200 items**, the generation automatically splits it into domain sub-files:

```
reforge_output/<project>/generated/
├── business-rules/
│   ├── index.html          # Sub-index for business rules
│   ├── validation.html     # Validation rules
│   ├── pricing.html        # Pricing rules
│   └── authorization.html  # Authorization rules
```

The sub-index page lists all domain groups with item counts and links to each sub-file. The master `index.html` links to the sub-index rather than a single large file.

!!! note
    The 200-item threshold applies per extraction type. Items are grouped by their category or domain classification within the extraction XML.

## Print-Friendly Styles

All HTML files include `@media print` styles:

- Navigation bars and interactive elements are hidden
- Page breaks are inserted at section boundaries
- Font sizes and margins are optimized for paper output
- Background colors are removed for clean printing
- Code blocks preserve their formatting with borders

## Source Provenance

Every generated section includes HTML comments tracing content back to the extraction XML:

```html
<!-- Source: business-rules.xml, rule id="BR-045" -->
```

This supports auditability -- you can trace any piece of generated documentation back to the specific extraction element that produced it.
