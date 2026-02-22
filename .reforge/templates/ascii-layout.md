# ASCII Layout Template

> Template for generating ASCII art UI layout representations from UI flow extractions

## Overview

ASCII layouts provide a text-based visualization of UI screens that:
- Works in any text editor or terminal
- Embeds directly in XML/markdown documentation
- Clearly shows component positioning
- Identifies interactive elements

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{screen.id}}` | UI extraction | Screen identifier |
| `{{screen.name}}` | UI extraction | Screen name |
| `{{screen.path}}` | UI extraction | URL/route |
| `{{screen.components}}` | UI extraction | UI components |
| `{{layout.rows}}` | Calculated | Layout height |
| `{{layout.columns}}` | Calculated | Layout width |

## ASCII Symbol Reference

### Container Elements

| Symbol | Description | Example |
|--------|-------------|---------|
| `+---+` | Box corner | `+----+` |
| `\|` | Vertical border | `\| content \|` |
| `---` | Horizontal border | `+------+` |
| `===` | Double border (header) | `+======+` |
| `- - -` | Dashed border (modal) | `+- - - -+` |

### Interactive Elements

| Symbol | Component | Example |
|--------|-----------|---------|
| `[Button]` | Button | `[Save] [Cancel]` |
| `[______]` | Text input | `Name: [__________]` |
| `[____v]` | Dropdown | `Status: [Active___v]` |
| `[x]` | Checkbox checked | `[x] Remember me` |
| `[ ]` | Checkbox unchecked | `[ ] Subscribe` |
| `(o)` | Radio selected | `(o) Option A` |
| `( )` | Radio unselected | `( ) Option B` |
| `[______|]` | Textarea | Multi-line input |

### Display Elements

| Symbol | Component | Example |
|--------|-----------|---------|
| `[IMG]` | Image | `[IMG: Logo]` |
| `[ICO]` | Icon | `[ICO:search]` |
| `<Link>` | Hyperlink | `<View Details>` |
| `...` | Truncated text | `Long text...` |
| `>>` | Navigation arrow | `Page 1 >> Page 2` |

### Layout Helpers

| Symbol | Description |
|--------|-------------|
| `\|--\|` | Column separator |
| `├──┤` | Row divider (table) |
| `«` `»` | Pagination |
| `▲` `▼` | Scroll indicators |
| `[+]` `[-]` | Expand/collapse |

## Layout Template

```
+{{repeat "-" (layout.columns - 2)}}+
|{{center screen.name layout.columns - 2}}|
+{{repeat "-" (layout.columns - 2)}}+
|                                          |
|  {{#each components}}                    |
|  {{render_component this}}               |
|  {{/each}}                               |
|                                          |
+{{repeat "-" (layout.columns - 2)}}+
```

## Component Rendering Rules

### Form Layout

```
+------------------------------------------+
|                 Form Title               |
+------------------------------------------+
|                                          |
|  Label:     [__________________]         |
|                                          |
|  Dropdown:  [Select option____v]         |
|                                          |
|  Checkbox:  [x] Option enabled           |
|                                          |
|  Radio:     (o) Choice A                 |
|             ( ) Choice B                 |
|             ( ) Choice C                 |
|                                          |
|            [Submit]    [Cancel]          |
+------------------------------------------+
```

### Table Layout

```
+------------------------------------------+
|  Header Column A  |  Col B  |  Actions   |
|-------------------|---------|------------|
|  Row 1 Data       |  Value  | [Ed] [Del] |
|  Row 2 Data       |  Value  | [Ed] [Del] |
|  Row 3 Data       |  Value  | [Ed] [Del] |
+------------------------------------------+
|  « Prev  |  Page 1 of 5  |  Next »      |
+------------------------------------------+
```

### Navigation Layout

```
+------------------------------------------+
|  [Logo]  | Home | Products | Cart (3)    |
+==========================================+
|  Breadcrumb: Home > Products > Item      |
+------------------------------------------+
```

### Modal/Dialog Layout

```
+- - - - - - - - - - - - - - - - - - - - - +
:                                           :
:           Confirm Delete                  :
:                                           :
:   Are you sure you want to delete         :
:   this item?                              :
:                                           :
:          [Delete]     [Cancel]            :
:                                           :
+- - - - - - - - - - - - - - - - - - - - - +
```

## Example Output

### Order List Screen

```
+============================================================+
|  [LOGO]    Search: [_______________] [Search]   [ICO:cart] |
+============================================================+
|  My Orders                                    [+ New Order] |
+------------------------------------------------------------+
|  ID     | Customer        | Total     | Status   | Actions |
|---------|-----------------|-----------|----------|---------|
|  #1001  | Acme Corp       | $1,250.00 | Shipped  | <View>  |
|  #1002  | Beta Inc        |   $500.00 | Pending  | <View>  |
|  #1003  | Gamma LLC       | $3,100.00 | Delivered| <View>  |
|  #1004  | Delta Co        |   $750.00 | Processing| <View> |
|  ...    | ...             | ...       | ...      | ...     |
+------------------------------------------------------------+
|  « Prev  |  Showing 1-10 of 156  |  Next »                 |
+------------------------------------------------------------+
```

### Order Form Screen

```
+============================================================+
|  [LOGO]    My Account                          [ICO:logout]|
+============================================================+
|  < Back to Orders                                          |
+------------------------------------------------------------+
|                      New Order                             |
+------------------------------------------------------------+
|                                                            |
|  Customer:   [Select customer___________v]                 |
|                                                            |
|  Items:      +----------------------------------+          |
|              | Product         | Qty  | Price   |          |
|              |-----------------|------|---------|          |
|              | Widget A        | [2_] | $50.00  |          |
|              | Gadget B        | [1_] | $100.00 |          |
|              | [+ Add Item]                     |          |
|              +----------------------------------+          |
|                                                            |
|  Shipping:   (o) Standard (5-7 days)                       |
|              ( ) Express (2-3 days) +$15                   |
|              ( ) Overnight +$30                            |
|                                                            |
|  Notes:      [____________________________________]        |
|              [____________________________________]        |
|              [____________________________________|]       |
|                                                            |
|  [x] Send confirmation email to customer                   |
|                                                            |
|  Subtotal:   $200.00                                       |
|  Discount:   -$20.00 (10% over $100)                       |
|  Shipping:   $0.00                                         |
|  -----------------------                                   |
|  Total:      $180.00                                       |
|                                                            |
|                   [Submit Order]    [Save Draft]           |
+------------------------------------------------------------+
```

### Login Screen

```
+----------------------------------+
|           [LOGO]                 |
|                                  |
|           Sign In                |
|                                  |
|  Email:    [__________________]  |
|                                  |
|  Password: [__________________]  |
|                                  |
|  [x] Remember me                 |
|                                  |
|         [Sign In]                |
|                                  |
|  <Forgot password?>              |
|  <Create account>                |
+----------------------------------+
```

## Generation Guidelines

### Source-Anchored Generation (Mandatory)

All generated ASCII layouts MUST comply with the Source-Anchored Generation constraints
defined in Step 0.6 of `.reforge/commands/generate.md`. Key obligations:

1. Extraction XML is the sole source of truth for all layout content
2. All identifiers (screen IDs, component IDs, labels) MUST be copied verbatim from extraction XML
3. All statistics (component counts, screen counts) MUST be computed with visible derivation formulas
4. `[DATA GAP]` markers MUST replace any content not supported by extraction data
5. Provenance annotations MUST cite extraction source files and element counts
6. The Content Validation Checklist MUST be completed before finalizing any layout output
7. The agent MUST NOT read source code files directly — all source context comes from extraction XML

When generating ASCII layouts:

1. **Use consistent widths** - Standard is 60-80 characters
2. **Align elements** - Use proper spacing for visual hierarchy
3. **Label interactive elements** - Show what each component does
4. **Include state** - Show selected/checked states where relevant
5. **Mark component IDs** - Reference back to extraction IDs
6. **Show data examples** - Use realistic placeholder data
