# /reforge.profile

> Generate a language-specific and architecture-specific extraction profile

## Command Syntax

```
/reforge.profile [--update]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--update` | No | Update existing profile — add/remove languages, architecture, or notes without replacing the entire file |

## Overview

This command gathers the project's technology stack (programming languages, frameworks,
architectural patterns) and generates a tailored extraction profile at
`.reforge/memory/extraction-profile.md`. The extract command loads this profile
automatically during initialization, providing language-specific and architecture-specific
guidance throughout the extraction process.

The profile command can auto-discover languages by scanning the codebase for file
extensions when the user does not declare them explicitly. The LLM generates extraction
rules for ANY declared language from its training knowledge — there is no finite
"supported languages" list.

## Workflow

### Step 0: Check Prerequisites

Verify that the `.reforge/memory/` directory exists. If it does not exist:
- Check if `.reforge/` exists at all
- If `.reforge/` is missing, instruct the user to run `/reforge.init` first or manually
  create the `.reforge/memory/` directory
- If `.reforge/` exists but `memory/` does not, create the `memory/` subdirectory

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents to:
- **Pre-populate language suggestions**: Extract languages from the Technology Stack section
  and present them as defaults in Step 2
- **Pre-populate architecture suggestions**: Extract architectural patterns from Custom Rules
  or Analysis Guidelines sections
- **Domain awareness**: Use domain knowledge to inform framework-specific guidance generation

If `project-context.md` does not exist, proceed without pre-population. Note to the user
that running `/reforge.init` first provides better defaults.

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Identify the item tagged `<!-- reforge:profile -->` and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:profile -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this operation. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Check Existing Profile

Read `.reforge/memory/extraction-profile.md` if it exists.

**If the file exists and `--update` was NOT specified:**
- Display a summary of the existing profile (languages, architecture, custom notes count)
- Ask the user: "An extraction profile already exists. Would you like to **update** it
  (add/remove items) or **replace** it entirely?"
- If user chooses update: proceed as if `--update` was specified
- If user chooses replace: proceed with a fresh profile (existing file will be overwritten)

**If the file exists and `--update` WAS specified:**
- Load the existing profile
- Parse current languages from `## Language-Specific Extraction Rules` subsection headings
- Parse current architecture from `## Architecture-Specific Extraction Guidance` subsection headings
- Parse current custom notes from `## Custom Extraction Notes` bullet items
- Present the current configuration to the user before gathering changes

**If the file does not exist:**
- Proceed directly to Step 2

### Step 2: Gather Languages

Ask the user to declare the programming languages used in the target codebase.

**Prompt:**
"What programming languages are used in this codebase? You can:
1. **Declare them**: List the languages (e.g., 'VB.NET 4.8, C#, SQL Server, COBOL')
2. **Auto-discover**: Type 'auto' and the agent will scan the codebase for file extensions
3. **Both**: Declare known languages, then auto-discover additional ones"

#### Auto-Discovery Sub-workflow

When the user requests auto-discovery (or does not declare any languages):

1. The agent MUST run Glob for common file extensions in the project root, respecting
   `.reforge/config.json` exclusion patterns. Use the following extension-to-language mapping
   as a starting point:

   **Modern languages:**
   `.cs` → C#, `.java` → Java, `.py` → Python, `.go` → Go, `.rs` → Rust,
   `.swift` → Swift, `.kt`/`.kts` → Kotlin, `.scala` → Scala, `.dart` → Dart, `.jl` → Julia

   **Web/scripting:**
   `.js`/`.mjs`/`.jsx` → JavaScript, `.ts`/`.tsx` → TypeScript, `.rb` → Ruby,
   `.php` → PHP, `.lua` → Lua, `.r` → R, `.pl`/`.pm` → Perl

   **Legacy/enterprise:**
   `.vb` → VB.NET, `.cob`/`.cbl` → COBOL, `.f`/`.f90`/`.f95`/`.f03` → Fortran,
   `.prg`/`.scx`/`.vcx`/`.frx` → FoxPro, `.asm`/`.s` → Assembly,
   `.rpgle`/`.rpg` → RPG, `.abap` → ABAP, `.bas` → BASIC, `.rex`/`.rexx` → REXX

   **Systems:**
   `.cpp`/`.cc`/`.c`/`.h`/`.hpp` → C/C++, `.adb`/`.ads` → Ada,
   `.pas`/`.dpr` → Delphi/Pascal, `.d` → D

   **Functional:**
   `.hs` → Haskell, `.erl` → Erlang, `.ex`/`.exs` → Elixir,
   `.clj`/`.cljs` → Clojure, `.ml`/`.mli` → OCaml, `.fs`/`.fsx` → F#

   **Data/query:**
   `.sql` → SQL, `.aspx`/`.ascx` → ASP.NET, `.groovy` → Groovy

   **Catch-all:** For any other file extensions found that the agent recognizes as source
   code for a programming language, include those languages as well. This list is a
   convenience mapping for Glob scanning — it is NOT a boundary on supported languages.

2. For ambiguous extensions (e.g., `.h` → C or C++, `.m` → MUMPS or Objective-C),
   present disambiguation options to the user.

3. Filter results to languages with significant file counts (e.g., >5 files) to reduce
   noise. Present ALL discovered languages sorted by file count.

4. Present discovered languages to the user for confirmation:
   ```
   Auto-discovered languages:
   - C# (247 files)
   - VB.NET (189 files)
   - SQL (56 files)
   - JavaScript (12 files)

   Confirm these languages? You can add or remove from this list.
   ```

5. The user confirms, adds, or removes from the discovered list. Users may declare ANY
   language manually even if no matching files were found (e.g., declaring COBOL when
   source files use non-standard extensions).

**In `--update` mode:** Present the current languages first, then allow the user to add
new ones or mark existing ones for removal. Unchanged languages retain their existing rules.

**If neither declaration nor auto-discovery produces any languages:**
Generate a minimal profile with only the General extraction rules section and any
architecture guidance or custom notes the user provides.

### Step 3: Gather Architecture Patterns

Ask the user about architectural styles used in the codebase.

**Prompt:**
"What architectural patterns does this codebase use? Common examples:
- **Layered / N-Tier**: Presentation → Business → Data layers
- **Microservices**: Independent services communicating via APIs/messages
- **Event-Driven**: Event sourcing, message bus, pub/sub patterns
- **Repository Pattern**: Abstracted data access via repository interfaces
- **Service Bus / ESB**: Enterprise service bus for integration
- **MVC / MVVM**: Model-View-Controller or Model-View-ViewModel
- **Monolithic**: Single deployable unit with internal module structure
- **CQRS**: Command Query Responsibility Segregation
- **Hexagonal / Clean Architecture**: Ports and adapters
- **Other**: Describe any other patterns

Type 'skip' if you don't want to declare architecture patterns."

For each declared pattern, the agent MUST generate guidance about:
- Where business rules typically reside in this architectural style
- Where data access patterns are found
- How to trace cross-layer or cross-service calls
- Where workflows and orchestration logic live
- Common integration points and boundaries

**In `--update` mode:** Present current architecture patterns, allow additions and removals.

### Step 4: Gather Custom Extraction Notes

Ask the user for project-specific extraction guidance.

**Prompt:**
"Do you have any project-specific extraction notes? These are custom guidelines
that help the agent extract more accurately. Examples:
- 'All business rules are in classes ending with Manager'
- 'Legacy COM interop wrappers in /Interop/ should be traced to original sources'
- 'The Enums/ directory contains custom enumeration base classes, not standard enums'
- 'Stored procedures prefixed with usp_ contain business logic; sp_ are system procedures'

Type 'skip' if you have no custom notes to add.
(Enter each note on a separate line. Press enter twice to finish)"

Record all user-provided notes verbatim.

**In `--update` mode:** Display existing custom notes, allow additions. Existing notes
are preserved unless the user explicitly requests removal.

### Step 5: Generate Extraction Profile

Write the extraction profile to `.reforge/memory/extraction-profile.md` using the
following structure:

```markdown
# Extraction Profile

Generated by `/reforge.profile` on YYYY-MM-DD
Languages: <comma-separated list of declared languages>
Architecture: <comma-separated list of declared patterns, or "Not specified">

## Language-Specific Extraction Rules

### <Language Name>
- **<Rule category>**: <Extraction guidance>
(Generate 5+ rules per language)
```

**Rule generation instructions for the agent:**

For EACH declared language — regardless of whether it is a modern, legacy, enterprise,
functional, or systems language — the agent MUST generate extraction rules from its
training knowledge covering these 5 categories:

1. **Type system quirks**: Language-specific type behaviors that affect extraction accuracy
   (e.g., VB.NET array upper bounds, COBOL PICTURE clauses, Fortran implicit typing)
2. **Operator differences**: Operators that could be misrecorded or paraphrased
   (e.g., VB.NET OrElse vs Or, COBOL COMPUTE vs MOVE, Assembly mnemonics)
3. **Naming conventions**: Case sensitivity rules and identifier patterns
   (e.g., COBOL SECTION/PARAGRAPH naming, Fortran case-insensitivity, RPG fixed-format fields)
4. **Common pitfalls**: Extraction errors specific to this language
   (e.g., FoxPro @ vs SAY commands, Assembly label vs instruction confusion, REXX stem variables)
5. **Framework patterns**: Framework-specific extraction guidance
   (e.g., COBOL CICS commands, Fortran MPI patterns, RPG RPG IV vs RPG III differences)

There is NO finite "supported languages" list. The LLM has training knowledge of virtually
all established programming languages. The same 5-category structure applies to C#, COBOL,
Fortran, Assembly, FoxPro, RPG, MUMPS, Ada, ABAP, Delphi, Haskell, or any other language.

For truly proprietary or internal DSLs where the LLM lacks training knowledge, generate
a section header with general guidance prompts and incorporate any details the user
provided in Step 4 (Custom Extraction Notes).

**Generate at least 5 rules per language.** For well-known languages, generate more
if the agent's knowledge supports it.

After the language rules, add:

```markdown
## Architecture-Specific Extraction Guidance

### <Pattern Name>
- **Business rules location**: <where business rules typically reside>
- **Data access location**: <where data access patterns are found>
- **Cross-layer calls**: <how to trace dependencies and calls across layers/services>
- **Workflow location**: <where orchestration and workflow logic lives>
- **Integration points**: <common integration boundaries and patterns>
```

Only include this section if the user declared architecture patterns in Step 3.

Then add:

```markdown
## Framework-Specific Patterns

### <Framework Name>
- <Framework-specific extraction patterns>
```

Only include this section if specific frameworks were declared alongside languages.

Finally, add:

```markdown
## Custom Extraction Notes
- <User-provided note 1>
- <User-provided note 2>
```

Only include this section if the user provided custom notes in Step 4.

**In `--update` mode:**
- Preserve all unchanged language sections — do NOT regenerate rules for languages
  that were not added or modified
- Regenerate rules only for newly added languages
- Remove sections for languages the user marked for removal
- Preserve existing custom notes and append new ones
- Preserve architecture guidance for unchanged patterns

### Step 6: Confirm and Suggest Next Steps

Display a summary of the generated profile:

```
Extraction profile generated at .reforge/memory/extraction-profile.md

Summary:
- Languages: <list>
- Architecture: <list or "None declared">
- Custom notes: <count> notes
- Total extraction rules: <count>

Next steps:
- Run `/reforge.extract [type]` to extract with language-specific guidance
- Run `/reforge.profile --update` to add or remove languages later
```
