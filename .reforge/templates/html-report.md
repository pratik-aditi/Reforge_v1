# HTML Report Template

> Master template for generating self-contained HTML documentation with the Stephen Few design system

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{project.name}}` | Config | Project name from `config.json` |
| `{{document.title}}` | Derived | Document title (e.g., "Business Rules Catalog") |
| `{{document.subtitle}}` | Derived | Document subtitle (e.g., "Extracted Business Logic and Decision Rules") |
| `{{document.date}}` | Generated | Generation date in `YYYY-MM-DD` format |
| `{{document.type}}` | Derived | Extraction type identifier (e.g., `business-rules`) |
| `{{sections}}` | Generated | Array of content sections |
| `{{toc_entries}}` | Generated | Table of contents entries |
| `{{diagrams}}` | Generated | Array of inline SVG diagrams |
| `{{provenance}}` | Computed | Source file provenance table rows |
| `{{nav_links}}` | Computed | Cross-document navigation links |
| `{{metrics}}` | Registry | Canonical metrics from metrics-registry.xml |

---

## A. CSS Design System (Stephen Few Style)

The following CSS MUST be embedded inline within a `<style>` tag in every generated HTML file. No external stylesheets are permitted.

```css
/* === Reforge HTML Report — Stephen Few Design System === */

:root {
  --ink: #1a1a1a;
  --ink-mid: #555;
  --ink-light: #888;
  --rule: #bbb;
  --rule-light: #ddd;
  --code-bg: #f7f7f5;
  --data: #2a6496;
  --data-light: #e8f0f8;
  --alert: #c0392b;
  --success: #27ae60;
  --bg: #fff;
}

*, *::before, *::after { box-sizing: border-box; }

html { font-size: 16px; -webkit-text-size-adjust: 100%; }

body {
  font-family: Georgia, 'Times New Roman', serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.65;
  max-width: 780px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* — Typography — */

h1 { font-size: 1.75rem; font-weight: 700; margin: 0 0 0.25rem; letter-spacing: -0.02em; }
h2 { font-size: 1.3rem; font-weight: 700; margin: 2.5rem 0 0.75rem; padding-bottom: 0.3rem; border-bottom: 2px solid var(--rule); }
h3 { font-size: 1.1rem; font-weight: 700; margin: 2rem 0 0.5rem; color: var(--ink); }
h4 { font-size: 0.95rem; font-weight: 700; margin: 1.5rem 0 0.4rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-mid); }

p { margin: 0 0 1rem; }
a { color: var(--data); text-decoration: none; border-bottom: 1px solid var(--data-light); }
a:hover { border-bottom-color: var(--data); }

/* — Labels & System UI — */

.label, .subtitle, .org, .date-range, nav, footer, figcaption, .toc a {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* — Code & Data — */

code, pre, .mono {
  font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace;
  font-size: 0.88rem;
}

code {
  background: var(--code-bg);
  padding: 0.15em 0.35em;
  border-radius: 3px;
}

pre {
  background: var(--code-bg);
  border: 1px solid var(--rule-light);
  border-radius: 4px;
  padding: 1rem 1.25rem;
  overflow-x: auto;
  line-height: 1.5;
  margin: 0 0 1.5rem;
}

pre code { background: none; padding: 0; }

/* — Report Header — */

.report-header {
  border-bottom: 3px solid var(--ink);
  padding-bottom: 1.25rem;
  margin-bottom: 2rem;
}

.report-header .org {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-mid);
  margin: 0 0 0.25rem;
}

.report-header .subtitle {
  font-size: 1rem;
  color: var(--ink-mid);
  margin: 0.25rem 0 0;
}

.report-header .date-range {
  font-size: 0.85rem;
  color: var(--ink-light);
  margin: 0.5rem 0 0;
}

/* — Callout Boxes — */

.callout {
  background: var(--data-light);
  border-left: 4px solid var(--data);
  padding: 1rem 1.25rem;
  margin: 1.5rem 0;
  border-radius: 0 4px 4px 0;
}

.callout p { margin: 0.25rem 0; }

.callout.warn {
  background: #fef9e7;
  border-left-color: #f39c12;
}

.callout.error {
  background: #fdedec;
  border-left-color: var(--alert);
}

/* — Table of Contents — */

.toc {
  column-count: 2;
  column-gap: 2rem;
  margin: 1rem 0 2rem;
  font-size: 0.9rem;
}

.toc ol {
  margin: 0;
  padding-left: 1.5em;
}

.toc li {
  margin: 0.3rem 0;
  break-inside: avoid;
}

.toc a {
  color: var(--ink);
  border-bottom: 1px solid var(--rule-light);
}

.toc a:hover { border-bottom-color: var(--data); color: var(--data); }

/* — Tables — */

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0 1.5rem;
  font-size: 0.9rem;
}

thead th {
  background: var(--code-bg);
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--ink-mid);
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid var(--rule);
}

tbody td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--rule-light);
  vertical-align: top;
}

tbody tr:hover { background: var(--data-light); }

/* — Badges — */

.sev, .conf, .cwe, .tag {
  display: inline-block;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.15em 0.5em;
  border-radius: 3px;
  vertical-align: middle;
}

/* Severity badges */
.sev { background: #eee; color: var(--ink-mid); }
.sev.crit { background: var(--alert); color: #fff; }
.sev.high { background: #e74c3c; color: #fff; }
.sev.med  { background: #f39c12; color: #fff; }
.sev.low  { background: #95a5a6; color: #fff; }

/* Confidence badges */
.conf { background: #eee; color: var(--ink-mid); }
.conf.high { background: var(--success); color: #fff; }
.conf.med  { background: #f39c12; color: #fff; }
.conf.low  { background: #e74c3c; color: #fff; }

/* CWE badges */
.cwe {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Tags */
.tag { background: var(--data-light); color: var(--data); }
.tag.p0 { background: var(--alert); color: #fff; }
.tag.p1 { background: #e74c3c; color: #fff; }
.tag.p2 { background: #95a5a6; color: #fff; }
.tag.flow { background: #d5f5e3; color: #1e8449; }
.tag.pattern { background: #fdebd0; color: #af601a; }

/* — Rule Detail Blocks — */

.rule-detail {
  border: 1px solid var(--rule-light);
  border-radius: 4px;
  padding: 1.25rem;
  margin: 1rem 0 1.5rem;
  background: #fafafa;
}

.rule-detail h4 { margin-top: 0; }

/* — Document Navigation — */

.doc-nav {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.85rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--rule-light);
  margin-bottom: 1.5rem;
  color: var(--ink-mid);
}

.doc-nav a {
  color: var(--data);
  margin: 0 0.4rem;
}

.doc-nav .current {
  font-weight: 700;
  color: var(--ink);
}

/* — Print Button — */

.print-btn {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.8rem;
  background: var(--ink);
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  z-index: 100;
}

.print-btn:hover { background: var(--ink-mid); }

/* — Report Footer — */

.report-footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--rule);
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.8rem;
  color: var(--ink-light);
}

/* — Diagram Styles — */

figure.diagram {
  margin: 1.5rem 0;
  text-align: center;
  cursor: pointer;
}

figure.diagram figcaption {
  font-size: 0.85rem;
  color: var(--ink-mid);
  margin-top: 0.5rem;
}

.diagram-svg {
  max-width: 100%;
  overflow: hidden;
  position: relative;
}

.diagram-svg svg {
  max-width: 100%;
  height: auto;
}

.diagram-svg.tall {
  max-height: 500px;
  overflow: hidden;
}

.diagram-svg.tall::after {
  content: 'Click to expand';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(transparent, var(--bg));
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 0.5rem;
  font-family: system-ui, sans-serif;
  font-size: 0.8rem;
  color: var(--data);
  pointer-events: none;
}

.flow-diagram {
  background: var(--code-bg);
  border: 1px solid var(--rule-light);
  border-radius: 4px;
  padding: 1rem;
  margin: 1rem 0;
}

/* — Lightbox Overlay — */

.diagram-lightbox {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9999;
  flex-direction: column;
}

.diagram-lightbox.active { display: flex; }

.lb-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-family: system-ui, sans-serif;
  font-size: 0.85rem;
}

.lb-controls button {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 0.3rem 0.6rem;
  margin-left: 0.4rem;
  border-radius: 3px;
  cursor: pointer;
  font-family: system-ui, sans-serif;
  font-size: 0.8rem;
}

.lb-controls button:hover {
  background: rgba(255,255,255,0.25);
}

.lb-inner {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.lb-inner svg {
  background: #fff;
  border-radius: 4px;
  max-width: none;
  transition: transform 0.15s ease;
}

.lb-hint {
  text-align: center;
  padding: 0.5rem;
  font-family: system-ui, sans-serif;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.5);
}

/* — Data Gap Markers — */

.data-gap {
  display: inline-block;
  background: #fef9e7;
  border: 1px dashed #f39c12;
  color: #856404;
  font-family: system-ui, sans-serif;
  font-size: 0.85rem;
  padding: 0.2em 0.5em;
  border-radius: 3px;
}

/* — Staleness Warning Banner — */

.staleness-warning {
  background: #fdedec;
  border: 1px solid #f5c6cb;
  color: var(--alert);
  font-family: system-ui, sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

/* — Print Styles — */

@media print {
  body {
    max-width: 100%;
    padding: 0;
    font-size: 11pt;
  }

  .print-btn, .doc-nav, .diagram-lightbox { display: none !important; }

  h2 { page-break-before: always; }
  h2:first-of-type { page-break-before: avoid; }
  h3, h4 { page-break-after: avoid; }

  table { page-break-inside: avoid; }
  .rule-detail { page-break-inside: avoid; }
  figure.diagram { page-break-inside: avoid; }

  .callout { border-left-width: 3px; }
  .report-header { border-bottom-width: 2px; }

  a { border-bottom: none; }
  a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.8em; color: var(--ink-light); }

  .diagram-svg.tall { max-height: none; overflow: visible; }
  .diagram-svg.tall::after { display: none; }
}

/* — Lightbox Scrollbar — */

.lb-inner::-webkit-scrollbar { width: 8px; height: 8px; }
.lb-inner::-webkit-scrollbar-track { background: rgba(255,255,255,0.1); }
.lb-inner::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.3); border-radius: 4px; }
```

---

## B. HTML Skeleton

Every generated HTML file MUST follow this structure. All CSS and JavaScript are inline — no external files.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{document.title}} — {{project.name}}</title>
  <style>
    /* [Insert complete CSS from Section A] */
  </style>
</head>
<body>

  <!-- Document Navigation -->
  <nav class="doc-nav">
    {{nav_links}}
  </nav>

  <!-- Report Header -->
  <header class="report-header">
    <p class="org">{{project.name}}</p>
    <h1>{{document.title}}</h1>
    <p class="subtitle">{{document.subtitle}}</p>
    <p class="date-range">Generated {{document.date}}</p>
  </header>

  <!-- Table of Contents -->
  <div class="toc">
    <ol>
      {{toc_entries}}
    </ol>
  </div>

  <!-- Content Sections -->
  {{#each sections}}
  <!-- Source: {{this.source_file}} ({{this.element_count}} {{this.element_type}}) -->
  <section id="{{this.id}}">
    <h2>{{this.title}}</h2>
    {{this.content}}
  </section>
  {{/each}}

  <!-- Provenance Footer -->
  <footer class="report-footer">
    <h4>Provenance</h4>
    <table>
      <thead>
        <tr>
          <th>Extraction File</th>
          <th>Element Type</th>
          <th>Count</th>
          <th>Last Modified</th>
        </tr>
      </thead>
      <tbody>
        {{provenance}}
      </tbody>
    </table>
    <p>Generated by Reforge · {{document.date}}</p>
  </footer>

  <!-- Print Button -->
  <button class="print-btn" onclick="window.print()">Print / PDF</button>

  <!-- Lightbox Element (only if document contains diagrams) -->
  {{#if diagrams}}
  <div class="diagram-lightbox" id="diagramLightbox">
    <div class="lb-toolbar">
      <span id="lbTitle"></span>
      <div class="lb-controls">
        <button onclick="lbZoom(-0.25)" title="Zoom out (−)">−</button>
        <button onclick="lbZoom(+0.25)" title="Zoom in (+)">+</button>
        <button onclick="lbFit()" title="Fit to view (F)">Fit</button>
        <button onclick="lbReset()" title="Actual size (0)">1:1</button>
        <button onclick="lbClose()" title="Close (Esc)">✕</button>
      </div>
    </div>
    <div class="lb-inner" id="lbInner"></div>
    <div class="lb-hint">Scroll to pan · Ctrl+wheel to zoom · Esc to close</div>
  </div>
  {{/if}}

  {{#if diagrams}}
  <!-- Lightbox JavaScript -->
  <script>
    /* [Insert complete JavaScript from Section C] */
  </script>
  {{/if}}

</body>
</html>
```

---

## C. Lightbox JavaScript

The following JavaScript MUST be included as an inline `<script>` in any HTML file that contains diagrams. It MUST be wrapped in an IIFE to avoid polluting the global scope.

```javascript
(function() {
  'use strict';

  var lightbox = document.getElementById('diagramLightbox');
  var lbInner  = document.getElementById('lbInner');
  var lbTitle  = document.getElementById('lbTitle');
  var scale    = 1;

  // Detect tall diagrams and add fade gradient
  document.querySelectorAll('figure.diagram .diagram-svg').forEach(function(el) {
    var svg = el.querySelector('svg');
    if (svg && svg.getBoundingClientRect().height > 500) {
      el.classList.add('tall');
    }
  });

  // Click-to-expand on diagram figures
  document.querySelectorAll('figure.diagram').forEach(function(fig) {
    fig.addEventListener('click', function() {
      var svgContainer = fig.querySelector('.diagram-svg');
      if (!svgContainer) return;
      var svg = svgContainer.querySelector('svg');
      if (!svg) return;

      var caption = fig.querySelector('figcaption');
      lbTitle.textContent = caption ? caption.textContent : 'Diagram';

      lbInner.innerHTML = '';
      var clone = svg.cloneNode(true);
      clone.style.maxWidth = 'none';
      clone.style.width = 'auto';
      clone.style.height = 'auto';
      lbInner.appendChild(clone);

      scale = 1;
      applyScale();
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  // Zoom controls
  window.lbZoom = function(delta) {
    scale = Math.max(0.25, Math.min(4, scale + delta));
    applyScale();
  };

  window.lbFit = function() {
    var svg = lbInner.querySelector('svg');
    if (!svg) return;
    var rect = svg.getBBox ? svg.getBBox() : { width: svg.scrollWidth, height: svg.scrollHeight };
    var cw = lbInner.clientWidth - 40;
    var ch = lbInner.clientHeight - 40;
    scale = Math.min(cw / rect.width, ch / rect.height, 1);
    applyScale();
  };

  window.lbReset = function() {
    scale = 1;
    applyScale();
  };

  window.lbClose = function() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  };

  function applyScale() {
    var svg = lbInner.querySelector('svg');
    if (svg) svg.style.transform = 'scale(' + scale + ')';
  }

  // Ctrl+wheel zoom
  lbInner.addEventListener('wheel', function(e) {
    if (e.ctrlKey) {
      e.preventDefault();
      lbZoom(e.deltaY < 0 ? 0.1 : -0.1);
    }
  }, { passive: false });

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    if (!lightbox.classList.contains('active')) return;
    switch (e.key) {
      case 'Escape': lbClose(); break;
      case '+': case '=': lbZoom(0.25); break;
      case '-': lbZoom(-0.25); break;
      case 'f': case 'F': lbFit(); break;
      case '0': lbReset(); break;
    }
  });

  // Click outside to close
  lightbox.addEventListener('click', function(e) {
    if (e.target === lightbox || e.target === lbInner) lbClose();
  });
})();
```

---

## D. PlantUML Rendering Instructions

When generating HTML reports, the agent MUST attempt to render PlantUML diagrams as inline SVG:

### Rendering Pipeline

1. **Generate PlantUML source** from extraction data (e.g., state diagrams from business rules, ERDs from database extractions)
2. **Render to SVG** using one of these methods (in priority order):
   - **Local PlantUML**: `plantuml -tsvg -pipe < input.puml > output.svg`
   - **PlantUML server**: POST to `http://www.plantuml.com/plantuml/svg/` (WebFetch)
   - **Fallback**: If rendering is unavailable, emit a gap marker
3. **Save .puml source** to `$DIAGRAMS_DIR/sources/{type}-{name}.puml`
4. **Embed SVG inline** in the HTML document

### Embedding Format

```html
<figure class="diagram" id="diagram-{{name}}">
  <div class="diagram-svg">
    <svg xmlns="http://www.w3.org/2000/svg" ...>
      <!-- inline SVG content -->
    </svg>
  </div>
  <figcaption>Figure N: {{caption}}</figcaption>
</figure>
```

### Fallback Gap Marker

If PlantUML rendering is unavailable:

```html
<figure class="diagram" id="diagram-{{name}}">
  <div class="data-gap">[DIAGRAM GAP: PlantUML rendering not available — source saved to $DIAGRAMS_DIR/sources/{{filename}}.puml]</div>
  <figcaption>Figure N: {{caption}}</figcaption>
</figure>
```

### Diagram Types by Extraction

| Extraction Type | Diagram Types | PlantUML Notation |
|---|---|---|
| `business-rules` | State diagrams, decision flows | `@startuml` with `state` or `if/else` |
| `database` | ERD diagrams | `@startuml` with `entity` |
| `ui` | Navigation flow diagrams | `@startuml` with `(*) --> (Screen)` |
| `workflows` | Sequence/activity diagrams | `@startuml` with `actor`/`participant` or `start`/`stop` |
| `call-sites` | Call graph diagrams | `@startuml` with directed links |
| `dependencies` | Module dependency diagrams | `@startuml` with `package` and `-->` |
| `non-functional` | Threat model diagrams | `@startuml` with `rectangle` and `-->` |
| `architecture` | C4/component diagrams | `@startuml` with C4 macros or `component` |
| `issues` | Impact diagrams | `@startuml` with `usecase` or `rectangle` |

---

## E. Badge/Tag Reference

The agent MUST use these badge classes consistently across all HTML documents:

### Confidence Badges

```html
<span class="conf high">HIGH</span>
<span class="conf med">MEDIUM</span>
<span class="conf low">LOW</span>
```

### Severity Badges

```html
<span class="sev crit">CRIT</span>
<span class="sev high">HIGH</span>
<span class="sev med">MEDIUM</span>
<span class="sev low">LOW</span>
```

### CWE Badges (Security)

```html
<span class="cwe">CWE-89</span>
<span class="cwe">CWE-79</span>
```

### General Tags

```html
<span class="tag">LABEL</span>
<span class="tag p0">CRITICAL</span>
<span class="tag p1">HIGH</span>
<span class="tag p2">LOW</span>
<span class="tag flow">FLOW NAME</span>
<span class="tag pattern">PATTERN</span>
```

### Data Gap Markers

```html
<span class="data-gap">[DATA GAP: description of missing data]</span>
```

### Derivation Formulas (Metrics)

```html
<span title="541 + 87 + 85 + 98 + 127">938</span>
```

---

## F. Multi-File Document Set Rules

When an extraction type produces a large volume of output, the agent MUST split it into multiple files:

### Splitting Thresholds

- **Item count > 200**: Split into domain/category sub-files
- **Estimated HTML > 300KB**: Split into domain/category sub-files

### File Naming Convention

| File Type | Pattern | Example |
|---|---|---|
| Master index | `index.html` | `index.html` |
| Per-type document | `{type}.html` | `business-rules.html` |
| Per-type sub-index | `{type}-index.html` | `business-rules-index.html` |
| Domain sub-file | `{type}-{domain}.html` | `business-rules-pricing.html` |

### Sub-Index Structure

When a type is split, the sub-index MUST contain:
- Same CSS design system (inline)
- Report header with type-specific title
- Summary statistics callout (total items, domains, coverage)
- Domain inventory table: domain name, item count, link to sub-file
- Navigation to master index and all sibling type documents

### Cross-Document Navigation

Every file in a document set MUST include `<nav class="doc-nav">` at two positions:
1. Below the report header (top navigation)
2. Above the report footer (bottom navigation)

Navigation format:

```html
<nav class="doc-nav">
  <a href="index.html">Index</a> ·
  <a href="business-rules.html">Business Rules</a> ·
  <span class="current">Database</span> ·
  <a href="ui.html">UI Flows</a> ·
  <a href="workflows.html">Workflows</a>
</nav>
```

- The current document name is rendered as `<span class="current">` (bold, no link)
- All other documents in the set are rendered as links
- The master index is always the first link
- Sub-files within a split type include links to their sub-index and all sibling sub-files

---

## Per-Type Document Content Guide

| Extraction Type | Document Title | Key Sections | Diagram Types |
|---|---|---|---|
| `business-rules` | Business Rules Catalog | By-category tables, rule detail blocks | State diagrams, decision flows |
| `database` | Data Dictionary | Entity tables, column details, relationships | ERD diagrams |
| `ui` | UI Screen Flows | Screen inventory, component tables, layouts | Navigation flow diagrams |
| `workflows` | Workflow Reference | Workflow inventory, step details, flow diagrams | Sequence/activity diagrams |
| `call-sites` | Call Site Analysis | Caller/callee tables, hot paths | Call graph diagrams |
| `dependencies` | Dependency Analysis | Module dependency tables, coupling metrics | Module dependency diagrams |
| `functional-requirements` | Functional Requirements | Requirements by category, acceptance criteria | — |
| `non-functional` | NFR & Security Reference | NFR tables with metrics, security findings with CWE | Threat model diagrams |
| `architecture` | Architecture Reference | Component inventory, integration points, patterns | C4/component diagrams |
| `issues` | Issues & Technical Debt | Bug tables, tech debt items, remediation roadmap | Impact diagrams |
